import os
import psycopg2
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import BaseModel
from typing import List
from datetime import datetime
from auth import get_auth_provider, AuthProvider, UserCreate
from jwt_utils import create_access_token
from jwt_utils import SECRET_KEY, ALGORITHM, TokenData
import jwt_utils

# Create an instance of the FastAPI class
app = FastAPI()

# Securely get the database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Pydantic model to define the structure of a POST request


class MessageCreate(BaseModel):
    content: str

# Helper function to get a database connection


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.on_event("startup")
async def startup_event():
    try:
        print("Attempting to connect to the database...")
        conn = get_db_connection()
        cur = conn.cursor()
        print("Database connection successful. Creating tables if they do not exist...")

        # This part is correct
        cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # --- ADD THIS PART ---
        # Create the 'users' table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL
            )
        ''')
        # --- END OF ADDED PART ---

        # Create the 'projects' table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        # --- END OF ADDED PART ---

        conn.commit()
        cur.close()
        conn.close()
        print("Startup complete. Tables are ready.")

    except Exception as e:
        print("!!! DATABASE CONNECTION FAILED !!!")
        print(f"Error: {e}")
        raise e

# Endpoint to create a new message (handles POST requests)


@app.post("/api/messages")
async def create_message(message: MessageCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Insert a new record into the messages table
        cur.execute("INSERT INTO messages (content) VALUES (%s)",
                    (message.content,))
        conn.commit()
        return {"status": "success", "message": "Message added"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# Endpoint to retrieve all messages (handles GET requests)


@app.get("/api/messages")
async def get_messages():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Select all records from the messages table, newest first
        cur.execute(
            "SELECT id, content, created_at FROM messages ORDER BY created_at DESC")
        messages = cur.fetchall()
        # Format the records as a list of dictionaries for JSON conversion
        messages_list = [{"id": msg[0], "content": msg[1],
                          "created_at": str(msg[2])} for msg in messages]
    finally:
        cur.close()
        conn.close()


# --- Authentication Endpoints ---

@app.post("/api/register")
async def register_user(user: UserCreate, auth: AuthProvider = Depends(get_auth_provider)):
    try:
        new_user = auth.register(user)
        return {"status": "success", "message": f"User '{new_user['username']}' registered."}
    except psycopg2.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/login")
async def login_user(user: UserCreate, auth: AuthProvider = Depends(get_auth_provider)):
    db_user = auth.login(user)
    if not db_user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")

    # Create a JWT token
    access_token = create_access_token(
        data={"sub": db_user['username']}
    )
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt_utils.jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    # You can add a step here to fetch the user from the database
    # if you need the full user object.
    return token_data


@app.get("/api/me")
async def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return {"username": current_user.username}

# Define a "route" or "endpoint"
# @app.get tells FastAPI that this function handles GET requests
# to the URL path "/api/hello"


@app.get("/api/hello")
async def hello_world():
    # FastAPI automatically converts Python dictionaries to JSON format
    return {"message": "Hello from you live FastAPI backend!"}

# Pydantic model for creating a project


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None

# Pydantic model for retrieving a project


class Project(ProjectCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


@app.post("/api/projects", response_model=Project)
async def create_project(project: ProjectCreate, current_user: TokenData = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get user_id from username
        cur.execute("SELECT id FROM users WHERE username = %s",
                    (current_user.username,))
        user_id = cur.fetchone()[0]

        # Insert a new record into the projects table
        cur.execute(
            "INSERT INTO projects (name, description, user_id) VALUES (%s, %s, %s) RETURNING id, name, description, user_id, created_at",
            (project.name, project.description, user_id)
        )
        new_project = cur.fetchone()
        conn.commit()
        return {"id": new_project[0], "name": new_project[1], "description": new_project[2], "user_id": new_project[3], "created_at": new_project[4]}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.get("/api/projects", response_model=List[Project])
async def get_projects(current_user: TokenData = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get user_id from username
        cur.execute("SELECT id FROM users WHERE username = %s",
                    (current_user.username,))
        user_id = cur.fetchone()[0]

        # Select all projects for the current user
        cur.execute(
            "SELECT id, name, description, user_id, created_at FROM projects WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        projects = cur.fetchall()
        projects_list = [{"id": p[0], "name": p[1], "description": p[2],
                          "user_id": p[3], "created_at": p[4]} for p in projects]
        return projects_list
    finally:
        cur.close()
        conn.close()

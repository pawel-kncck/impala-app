import os
import psycopg2
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from auth import get_auth_provider, AuthProvider, UserCreate, UserUpdate
from jwt_utils import create_access_token
from jwt_utils import SECRET_KEY, ALGORITHM, TokenData
import jwt_utils
from fastapi import UploadFile, File
import pandas as pd
import shutil
from database_mongo import get_database
from bson import ObjectId
from pymongo.errors import PyMongoError

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
                hashed_password TEXT NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50)
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

        # Create the 'data_sources' table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

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
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, username, first_name, last_name FROM users WHERE username = %s",
            (current_user.username,)
        )
        user = cur.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user[0], "username": user[1], "first_name": user[2], "last_name": user[3]}
    finally:
        cur.close()
        conn.close()


@app.put("/api/me/update")
async def update_user_me(user_update: UserUpdate, current_user: TokenData = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE users SET first_name = %s, last_name = %s WHERE username = %s RETURNING id, username, first_name, last_name",
            (user_update.first_name, user_update.last_name, current_user.username)
        )
        updated_user = cur.fetchone()
        conn.commit()
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": updated_user[0], "username": updated_user[1], "first_name": updated_user[2], "last_name": updated_user[3]}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

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


class DataSource(BaseModel):
    id: int
    project_id: int
    file_name: str
    created_at: datetime

    class Config:
        orm_mode = True

# Pydantic model for creating a canvas


class CanvasCreate(BaseModel):
    name: str
    content: dict = {}

# Pydantic model for retrieving a canvas


class Canvas(CanvasCreate):
    id: str
    project_id: int
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


@app.post("/api/projects/{project_id}/upload-csv")
async def upload_csv(project_id: int, file: UploadFile = File(...), current_user: TokenData = Depends(get_current_user)):
    # Ensure the uploads directory exists
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Basic validation of the CSV file
    try:
        # Read the file in chunks to avoid memory issues with large files
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {e}")
    finally:
        # Reset the file pointer to the beginning
        file.file.seek(0)

    # Save the uploaded file
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Create a record in the data_sources table
        cur.execute(
            "INSERT INTO data_sources (project_id, file_name, file_path) VALUES (%s, %s, %s) RETURNING id, project_id, file_name, created_at",
            (project_id, file.filename, file_path)
        )
        new_data_source = cur.fetchone()
        conn.commit()
        return {"id": new_data_source[0], "project_id": new_data_source[1], "file_name": new_data_source[2], "created_at": new_data_source[3]}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.get("/api/projects/{project_id}/data-sources", response_model=List[DataSource])
async def get_data_sources(project_id: int, current_user: TokenData = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, project_id, file_name, created_at FROM data_sources WHERE project_id = %s ORDER BY created_at DESC",
            (project_id,)
        )
        data_sources = cur.fetchall()
        data_sources_list = [{"id": ds[0], "project_id": ds[1],
                              "file_name": ds[2], "created_at": ds[3]} for ds in data_sources]
        return data_sources_list
    finally:
        cur.close()
        conn.close()


@app.post("/api/projects/{project_id}/canvases", response_model=Canvas)
async def create_canvas(project_id: int, canvas: CanvasCreate, current_user: TokenData = Depends(get_current_user)):
    db = get_database()
    try:
        # You might want to verify that the project belongs to the current user first
        # (omitted for brevity)

        canvas_doc = {
            "project_id": project_id,
            "name": canvas.name,
            "content": canvas.content,
            "created_at": datetime.now()
        }
        result = db.canvases.insert_one(canvas_doc)
        created_canvas = db.canvases.find_one({"_id": result.inserted_id})

        # Convert ObjectId to string for the response model
        created_canvas["id"] = str(created_canvas["_id"])

        return created_canvas
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/canvases", response_model=List[Canvas])
async def get_canvases(project_id: int, current_user: TokenData = Depends(get_current_user)):
    db = get_database()
    try:
        canvases = []
        for canvas in db.canvases.find({"project_id": project_id}):
            canvas["id"] = str(canvas["_id"])
            canvases.append(canvas)
        return canvases
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/canvases/{canvas_id}", response_model=Canvas)
async def update_canvas(canvas_id: str, canvas_update: CanvasCreate, current_user: TokenData = Depends(get_current_user)):
    db = get_database()
    try:
        updated_doc = {
            "name": canvas_update.name,
            "content": canvas_update.content,
        }
        result = db.canvases.update_one(
            {"_id": ObjectId(canvas_id)},
            {"$set": updated_doc}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Canvas not found")

        updated_canvas = db.canvases.find_one({"_id": ObjectId(canvas_id)})
        updated_canvas["id"] = str(updated_canvas["_id"])
        return updated_canvas

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid canvas ID")


@app.delete("/api/canvases/{canvas_id}", status_code=204)
async def delete_canvas(canvas_id: str, current_user: TokenData = Depends(get_current_user)):
    db = get_database()
    try:
        result = db.canvases.delete_one({"_id": ObjectId(canvas_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Canvas not found")
        return
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid canvas ID")

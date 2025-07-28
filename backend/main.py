import os
import psycopg2
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
# Import our new components
from auth import get_auth_provider, AuthProvider, UserCreate

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

    # In Project 3, we will generate a JWT here
    return {"status": "success", "message": "Login successful"}


# Define a "route" or "endpoint"
# @app.get tells FastAPI that this function handles GET requests
# to the URL path "/api/hello"


@app.get("/api/hello")
async def hello_world():
    # FastAPI automatically converts Python dictionaries to JSON format
    return {"message": "Hello from you live FastAPI backend!"}

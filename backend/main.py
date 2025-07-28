import os
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

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
        print("Database connection successful. Creating table if it does not exist...")

        cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Startup complete. Table 'messages' is ready.")

    except Exception as e:
        # This will print the exact error to your Render logs
        print("!!! DATABASE CONNECTION FAILED !!!")
        print(f"Error: {e}")
        # Re-raise the exception to ensure the app still fails to start
        # This prevents the app from running in a broken state.
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

# Define a "route" or "endpoint"
# @app.get tells FastAPI that this function handles GET requests
# to the URL path "/api/hello"


@app.get("/api/hello")
async def hello_world():
    # FastAPI automatically converts Python dictionaries to JSON format
    return {"message": "Hello from you live FastAPI backend!"}

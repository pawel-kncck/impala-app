from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
import psycopg2
import os

# --- Pydantic Models for Data Transfer ---


class UserCreate(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# --- Password Hashing (Keep this for the local provider) ---


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

# --- Abstract Base Class for Auth Providers ---


class AuthProvider(ABC):
    @abstractmethod
    def register(self, user: UserCreate):
        pass

    @abstractmethod
    def login(self, user: UserCreate):
        pass

# --- PostgreSQL Implementation of the Auth Provider ---


class PostgresAuthProvider(AuthProvider):
    def get_db_connection(self):
        DATABASE_URL = os.environ.get('DATABASE_URL')
        return psycopg2.connect(DATABASE_URL)

    def register(self, user: UserCreate):
        conn = self.get_db_connection()
        cur = conn.cursor()
        try:
            hashed_password = get_password_hash(user.password)
            cur.execute(
                "INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id",
                (user.username, hashed_password)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            return {"id": user_id, "username": user.username}
        finally:
            cur.close()
            conn.close()

    def login(self, user: UserCreate):
        conn = self.get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, username, hashed_password FROM users WHERE username = %s", (user.username,))
            db_user = cur.fetchone()

            if not db_user or not verify_password(user.password, db_user[2]):
                return None

            return {"id": db_user[0], "username": db_user[1]}
        finally:
            cur.close()
            conn.close()

# --- Future Firebase Implementation (Example) ---
# You would build this out when you're ready to switch.

# class FirebaseAuthProvider(AuthProvider):
#     def register(self, user: UserCreate):
#         # ... Firebase registration logic here ...
#         pass
#
#     def login(self, user: UserCreate):
#         # ... Firebase login logic here ...
#         pass

# --- Dependency for FastAPI ---
# This makes it easy to switch providers in one place.


def get_auth_provider():
    # To switch to Firebase later, you'd just change this one line:
    # return FirebaseAuthProvider()
    return PostgresAuthProvider()

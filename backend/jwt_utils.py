import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from pydantic import BaseModel

# --- Configuration ---
# It's better to use environment variables for this
SECRET_KEY = os.environ.get('SECRET_KEY', 'a_super_secret_key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class TokenData(BaseModel):
    username: str | None = None


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

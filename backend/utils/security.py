from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from ..config import settings
from ..database import get_db_connection


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
# Use bcrypt as preferred, but include pbkdf2_sha256 as a fallback so
# development environments without a working bcrypt backend can still
# create and verify passwords. In production you should ensure bcrypt
# is installed and used.
password_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
   try:
      return password_context.hash(password)
   except Exception as e:
      # If bcrypt backend isn't available, fall back to pbkdf2_sha256 explicitly
      try:
         return password_context.hash(password, scheme="pbkdf2_sha256")
      except Exception:
         # Let caller handle any further exceptions
         raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
   return password_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
   to_encode = data.copy()
   if expires_delta:
       expire = datetime.now(timezone.utc) + expires_delta
   else:
       expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
   to_encode["exp"] = expire
   return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def authenticate_user(username: str, password: str):
   conn = get_db_connection()
   user = conn.execute("SELECT * FROM User WHERE user_name = ?", (username,)).fetchone()
   conn.close()

   return user if user and verify_password(password, user["password"]) else None

def get_current_user(token: str = Depends(oauth2_scheme)):
   try:
      payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
      username = payload.get("sub")
      if username is None:
          raise HTTPException(status_code=401, detail="Invalid authentication credentials")
      print(username)
   except jwt.PyJWTError as e:
      raise HTTPException(status_code=401,
                          detail="Invalid authentication credentials") from e

   conn = get_db_connection()
   user = conn.execute("SELECT * FROM User WHERE user_name = ?", (username,)).fetchone()
   conn.close()

   if user is None:
       raise HTTPException(status_code=401, detail="User not found")
   return dict(user)
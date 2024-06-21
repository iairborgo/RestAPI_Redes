from pydantic import BaseModel
from typing import Optional, Union, Annotated
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from jwt.exceptions import InvalidTokenError
from fastapi import  status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import pandas as pd

SECRET_KEY = 'f78acc76c3f665c960454dffd51010b6' # mock 
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRES_MIN = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class Libro(BaseModel):
    author: Optional[str] = 'Unknown'
    country: str
    imageLink: Union[str | None] = None
    language: str
    link: str
    pages: int
    title: str
    year: int

class Usuario(BaseModel):
    user: str
    password: str

pwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

class Hash():
    def bcrypt(password : str):
        return pwd_context.hash(password)
    def autenticar(password : str, hashed : str):
        return pwd_context.verify(password, hashed)

class Login(BaseModel):
    user: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MIN)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

def load_data():
    df_libros = pd.read_json('books.json')
    df_imagepath= pd.read_json('booksimagepath.json')
    df_usuarios = pd.read_json('users.json')
    return df_libros, df_imagepath, df_usuarios

from pwdlib import PasswordHash
import uuid
from datetime import datetime,timedelta,timezone
import jwt
import hashlib
from app.config import settings
from typing import Annotated
from fastapi import Depends
from app.config import settings
from fastapi import status
from fastapi import HTTPException
from app.db import DbSession
from sqlalchemy import select
from app.models import User
import secrets

#need to install python-multipart for oauth2
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

password_hasher=PasswordHash.recommended()

def hash_password(password:str)->str:
    hashed_password=password_hasher.hash(password)
    return hashed_password

def verify_password(password:str,password_hash:str)->bool:
    return password_hasher.verify(password,password_hash)

def create_access_token(user_id:uuid.UUID)->str:
    expire=datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_expire_minutes)
    payload={"sub":str(user_id),"exp":expire}
    token=jwt.encode(payload,settings.secret_key,algorithm=settings.algorithm)
    return token

def decode_access_token(token:str):
        payload=jwt.decode(token,settings.secret_key,algorithms=[settings.algorithm],options={"require":["sub","exp"]})
        return uuid.UUID(payload["sub"])

async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:DbSession)->User:
    
    try:
        user_id=decode_access_token(token=token)
    except jwt.InvalidTokenError, ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials/Could not validate credentials",
            headers={"WWW-Authenticate":"Bearer"}

        )
    user=(await db.execute(select(User).where(User.id==user_id))).scalar_one_or_none()
    if user is None:
        #this would expose which user's have accounts so DON'T do this...
        # raise HTTPException(
        #     status=status.HTTP_404_NOT_FOUND,
        #     detail="User couldn't be found"
        # )
        #instead raise the same error as for jwt.InvalidTokenError,ValueError so hackers won't know
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials/Could not validate credentials",
            headers={"WWW-Authenticate":"Bearer"}

        )
    return user
    
CurrentUser=Annotated[User,Depends(get_current_user)]


def create_refresh_token()->str:
    return secrets.token_urlsafe(32)

def hash_token(token:str)->str:
    return hashlib.sha256(token.encode()).hexdigest()

#.encode() converts the text str into raw bytes(0s and 1s), hashing algos operate on raw bytes
#hashlib.sha256() hashes the raw bytes ,returns a hash object,not readable text sha256 algorithm used
#.hexdigest() converts that into text,a string containing only no's 0-9 and letters a-z
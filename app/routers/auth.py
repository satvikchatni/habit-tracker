import asyncio
from fastapi import APIRouter,HTTPException,status,Depends
from sqlalchemy.exc import IntegrityError
from app.db import DbSession
from app.schemas import RegisterRequest,UserResponse,TokenResponse
from app.models import User
from app.security import hash_password,verify_password,create_access_token
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
router=APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def register(db:DbSession,body:RegisterRequest):
    hashed_password=await asyncio.to_thread(hash_password,body.password)
    user=User(email=body.email.lower(),password_hash=hashed_password)
    await db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login",response_model=TokenResponse,status_code=status.HTTP_200_OK)
async def login(db:DbSession,form:Annotated[OAuth2PasswordRequestForm,Depends(OAuth2PasswordRequestForm)]):
    query=select(User).where(User.email==form.username.lower())
    result = await db.execute(query)
    user=result.scalar_one_or_none()
    if not user or not await asyncio.to_thread(verify_password,form.password,user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate":"Bearer"}
        )
    access_token=create_access_token(user.id)
    return access_token



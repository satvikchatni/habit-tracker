import asyncio
from fastapi import APIRouter,HTTPException,status,Depends
from sqlalchemy.exc import IntegrityError
from app.db import DbSession
from app.schemas import RegisterRequest,UserResponse,TokenResponse,RefreshRequest
from app.models import User,RefreshToken
from app.security import hash_password,verify_password,create_access_token,hash_token,create_refresh_token,CurrentUser,issue_refresh_token,revoke_family
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from datetime import datetime,UTC
router=APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def register(db:DbSession,body:RegisterRequest):
    hashed_password=await asyncio.to_thread(hash_password,body.password)
    user=User(email=body.email.lower(),password_hash=hashed_password)
    db.add(user)
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
    refresh_token=await issue_refresh_token(db=db,user_id=user.id)
    await db.commit()
    return TokenResponse(access_token=access_token,refresh_token=refresh_token)

@router.post("/refresh",response_model=TokenResponse)
async def refresh_route(db:DbSession,body:RefreshRequest):
    invalid=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials",headers={"WWW-Authenticate":"Bearer"})
    stored=(await db.execute(select(RefreshToken).where(RefreshToken.token_hash==hash_token(body.refresh_token)))).scalar_one_or_none()
    if stored is None: #that refresh token doesn't exist
        raise invalid
    if stored.revoked_at is not None:#refresh token has already been used and its been revoked too
        #might be stolen,best to end current session for all devices/logout for every device
        await revoke_family(db=db,family_id=stored.family_id)
        await db.commit()
        raise invalid
    if stored.expired_at<=datetime.now(UTC):
        raise invalid

    #RTR:refresh token rotation

    stored.revoked_at=datetime.now(UTC)
    new_refresh_token=await issue_refresh_token(db=db,user_id=stored.user_id)
    await db.commit()
    return TokenResponse(access_token=create_access_token(stored.user_id),refresh_token=new_refresh_token)


@router.post("/logout")
async def logout_user(db:DbSession,body:RefreshRequest):
    stored=(await db.execute(select(RefreshToken).where(RefreshToken.token_hash==hash_token(body.refresh_token)))).scalar_one_or_none()
    if stored is not None:
        await revoke_family(db,stored.family_id)
        await db.commit()






from pydantic import BaseModel,field_validator,ConfigDict,EmailStr,Field
import uuid
from datetime import datetime,date
class HabitCreate(BaseModel):

    name:str

class HabitOut(HabitCreate):
    id:uuid.UUID
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)
class CheckinCreate(BaseModel):
    
    day:date|None=None

class CheckinOut(CheckinCreate):
    id:uuid.UUID
    created_at:datetime
    habit_id:uuid.UUID
    model_config=ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    email:EmailStr
    password:str=Field(min_length=8,max_length=128)

class UserResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:uuid.UUID
    email:EmailStr
    created_at:datetime

class TokenResponse(BaseModel):
    access_token:str
    token_type:str="bearer"
    
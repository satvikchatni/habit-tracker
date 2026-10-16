from fastapi import APIRouter,status,HTTPException
from app.db import DbSession
from app.schemas import HabitCreate,HabitOut,CheckinOut,CheckinCreate
from app import models
from sqlalchemy import select
import uuid
from datetime import datetime,timezone
from sqlalchemy.exc import IntegrityError
router=APIRouter(prefix="/habits",tags=["habits"])


@router.post("/",status_code=status.HTTP_201_CREATED,response_model=HabitOut)
async def the_habit(body:HabitCreate,db:DbSession):
    name=body.name
    if name.strip()=="" or len(name)>100:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,detail="name either too long or empty")
    new_habit=models.Habits(name=name)
    await db.add(new_habit)
    await db.commit()
    await db.refresh(new_habit)
    return new_habit

@router.get("/",response_model=list[HabitOut])
async def list_of_habits(db:DbSession):
    result= await db.execute(select(models.Habits).order_by(models.Habits.created_at.asc()))
    return result.scalars().all()

@router.get("/{habit_id}",status_code=status.HTTP_200_OK)
async def habit_by_id(db:DbSession,habit_id:uuid.UUID):
    habit=select(models.Habits).where(models.Habits.id==habit_id)
    res=(await db.execute(habit)).scalar_one_or_none()
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"habit with id={habit_id} doesn't exist")
    return res

@router.delete("/{habit_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(habit_id:uuid.UUID,db:DbSession):
    query=select(models.Habits).where(models.Habits.id==habit_id)
    habit=(await db.execute(query)).scalar_one_or_none()
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ID Not found")
    await db.delete(habit)
    await db.commit()
    return None #204 content requires returning None

@router.post("/{habit_id}/checkins",status_code=status.HTTP_201_CREATED,response_model=CheckinOut)
async def habit_checkin(db:DbSession,habit_id:uuid.UUID,body:CheckinCreate):
    q=select(models.Habits).where(models.Habits.id==habit_id)
    habit=(await db.execute(q)).scalar_one_or_none()
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ID not found")
    target_day=body.day if(body and body.day) else datetime.now(timezone.utc).date()
    checkin=models.Checkins(habit_id=habit_id,day=target_day)
    try:
        await db.add(checkin)
        await db.commit()
        await db.refresh(checkin)
        return checkin
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="already checked in for this habit on this day"
        )
    

    


@router.get("/{habit_id}/checkins",status_code=status.HTTP_200_OK,response_model=list[CheckinOut])
async def get_checkin(db:DbSession,habit_id:uuid.UUID):
    query=select(models.Habits).where(models.Habits.id==habit_id)
    habit=(await db.execute(query)).scalar_one_or_none()
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="ID Not found")
    
    checkin_query=select(models.Checkins).where(models.Checkins.habit_id==habit_id).order_by(models.Checkins.created_at.desc())
    result=(await db.execute(checkin_query))
    return result.scalars().all()


    




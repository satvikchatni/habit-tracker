import uuid
from datetime import datetime,date,timezone
from sqlalchemy import TIMESTAMP,text,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from app.db import Base

class User(Base):
    __tablename__="users"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    email:Mapped[str]=mapped_column(unique=True)
    password_hash:Mapped[str]=mapped_column(nullable=False)
    created_at:Mapped[datetime]=mapped_column(
        TIMESTAMP(timezone=True),nullable=False,server_default=text('now()')
    )

class Habits(Base):
    __tablename__="habits"
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    name:Mapped[str]=mapped_column(nullable=False)
    created_at:Mapped[datetime]=mapped_column(TIMESTAMP(timezone=True),server_default=text('now()'))

class Checkins(Base):
    __tablename__="checkins"
    id:Mapped[uuid.UUID]=mapped_column(default=uuid.uuid4,primary_key=True)
    habit_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("habits.id",ondelete="CASCADE"),unique=True)
    day:Mapped[date]=mapped_column(default=datetime.now(timezone.utc).date())
    created_at:Mapped[datetime]=mapped_column(TIMESTAMP(timezone=True),server_default=text('now()'))
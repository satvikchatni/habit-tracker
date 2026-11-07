from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.db import DbSession, engine
from app.routers import auth, habits


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(habits.router)
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Hello world!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
async def health_check_db(db: DbSession):
    await db.execute(text("SELECT 1"))
    return {"database": "ok"}

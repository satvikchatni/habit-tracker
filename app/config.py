from pydantic_settings import BaseSettings,SettingsConfigDict
from sqlalchemy import URL
from pydantic import Field
#can use from app.config import settings in any file and then use the env variables without exposing sensitive info.

class Settings(BaseSettings):
    database_user:str
    database_port:int
    database_host:str
    database_password:str
    database_name:str
    secret_key:str=Field(min_length=32)
    access_token_expire_minutes:int=15
    algorithm:str="HS256"
    

    
    
    @property
    def database_url(self)->URL:
        return URL.create(
            drivername='postgresql+asyncpg',
            username=self.database_user,
            password= self.database_password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name
            )

    
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")



settings=Settings()
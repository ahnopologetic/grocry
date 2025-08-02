from pydantic_settings import BaseSettings


class Config(BaseSettings):
    database_url: str = "sqlite:///./grocry.db"

    class Config:
        env_file = ".env"


config = Config()

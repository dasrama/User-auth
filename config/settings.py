from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE: str
    POSTGRES_HOST: int
    POSTGRES_PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


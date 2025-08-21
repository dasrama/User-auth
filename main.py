from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncpg

from config.settings import Setting


async def get_postgres_cursor():
    conn = asyncpg.connect(
        user=Setting().POSTGRES_USER,
        password=Setting().POSTGRES_PASSWORD,
        database=Setting().POSTGRES_DATABASE,
        host=Setting().POSTGRES_HOST,
        port=Setting().POSTGRES_PORT
    )

app = FastAPI()


app.post("/login")
async def login(request: Request):
    if not request.auth:
        return JSONResponse(
            status_code=401,
            content={
                "status": "401 unauthorized",
                "error": "authentication error",
                "message": "please authenticate first"
            }
        )
    

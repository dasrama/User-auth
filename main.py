import asyncpg
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

from config.config import get_postgres_cursor
from schemas.user import User


app = FastAPI()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def generate_hashed_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str)-> bool:
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/register")
async def register(user: User, db: asyncpg.Connection = Depends(get_postgres_cursor)):
    try:
        existing_user = await db.fetchrow('SELECT email from users where email=$1', user.email)
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={
                    "status": f"user with email {user.email} already exists",
                    "error": "Bad Request",
                    "data": None
                }
            )
        
        hashed_password = generate_hashed_password(user.password)

        await db.execute(
            "INSERT INTO users (email, password) VALUES ($1, $2)",
            user.email, hashed_password
        )

        return JSONResponse(
            status_code=201,
            content={
                "status": "User registered successfully",
                "error": None,
                "data": {"email": user.email}
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "data": None
            }
        )
        

@app.post("/login")
async def login(request: Request, db: asyncpg.Connection = Depends(get_postgres_cursor)):
    auth_header = request.headers.get("Authorization")
     
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={
                "status": "401 unauthorized",
                "error": "authentication error",
                "message": "please authenticate first"
            }
        )
    
    body = await request.json()
    email = body.get("email")

    query = "SELECT email, password FROM users WHERE email=$1"
    result = await db.fetchrow(query, email)

    if not result:
        return JSONResponse(
            status_code=404,
            content={
                "error": "User not found in database",
                "data": None,
                "status": "Not Found"
            }
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "successfully logged in",
            "error": None,
            "data": {
                "email": email
            }
        }
    )
    
import asyncpg
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse

from config.config import get_postgres_cursor
from schemas.user import User
from utils.auth import AuthSecurity


app = FastAPI()

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
        
        hashed_password = AuthSecurity.generate_hashed_password(user.password)

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

# JWT --> headers (algo+type) + payload (user info such as user_id, username, expiry time, role) + signature    

@app.post("/login")
async def login(user: User, db: asyncpg.Connection = Depends(get_postgres_cursor)):
    try:
        user_data = await db.fetchrow('SELECT * FROM users WHERE email = $1', user.email)
        if not user_data:
            return JSONResponse(
                status_code=401,
                content={
                    "status": "401 unauthorized",
                    "error": "authentication error",
                    "message": "Please register your email"
                }
            )
        
        valid_password = AuthSecurity.verify_password(user.password, user_data["password"])
        if not valid_password:
            return JSONResponse(
                status_code=401,
                content={
                    "status": "401 unauthorized",
                    "error": "authentication error",
                    "message": "Invalid password"
                }
            )

        # create token with correct payload
        access_token = AuthSecurity.create_access_token(
            user_data={"email": user_data["email"], "user_id": user_data["id"]}
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": "successfully logged in",
                "error": None,
                "data": {
                    "token": access_token
                }
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "internal server error",
                "error": str(e),
                "data": None
            }
        )

    
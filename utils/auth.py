from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import jwt
from config.settings import Setting

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRY = 3600


class AuthSecurity:

    @staticmethod    
    def generate_hashed_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str)-> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_data: dict, expiry: timedelta = None, refresh : bool = False):
        expire_time = datetime.now(timezone.utc) + (expiry if expiry else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
        payload = {
            "user": user_data["user_id"],
            "email": user_data["email"],
            "exp": int(expire_time.timestamp())
        }

        token =  jwt.encode(
            payload=payload,
            key=Setting().JWT_SECRET_KEY,
            algorithm="HS256"
        )

        return token
    
    @staticmethod
    def decode_token(token: str)-> dict:
        try:
            token_data = jwt.decode(
                jwt=token,
                key=Setting().JWT_SECRET_KEY,
                algorithms=['HS256']
            )

            return token_data
        
        except jwt.PyJWTError as e:
            return None     

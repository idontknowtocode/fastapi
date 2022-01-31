import jwt
from dotenv import dotenv_values
from passlib.context import CryptContext
from models import *
from fastapi import status,HTTPException

pwd_context = CryptContext(schemes = ['bcrypt'],deprecated = "auto")
config_credentials = dotenv_values(".env")

def get_hashed_password(password):
    return pwd_context.hash(password)

async def verify_token(token:str):
    try:
        payload = jwt.decode(token,config_credentials["SECRET"],algorithms = ['HS256'])
        user = await User.get(id=payload.get("id"))
    except:
        raise HTTPException(
            status_code =status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Token",
            headers = {"WWW-Authenticate":"Bearer"}
        )
    return user

async def verify_password(password,hashed_password):
    return await pwd_context.verify(password,hashed_password)

async def authenticate_user(username,password):
    user = await User.get(username=username)
    if user and verify_password(password,user.password):
        return True,user
    return False,None

async def token_generator(username :str,password:str):
    res, user = await authenticate_user(username,password)
    if not res:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid username or password",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    if user!=None :   
        token_data={
            "id": user.id,
            "username" :user.username,
        }
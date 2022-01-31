import dotenv
from fastapi import (BackgroundTasks,UploadFile, File,Form, Depends,HTTPException, status)
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
import dotenv
import jwt
from pydantic import BaseModel,EmailStr
from models import User

config_credentials = dotenv.dotenv_values(".env")

conf = ConnectionConfig(
    MAIL_USERNAME = config_credentials["EMAIL"],
    MAIL_PASSWORD = config_credentials["PASSWORD"],
    MAIL_FROM = config_credentials["EMAIL"],
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True  
)


class EmailSchema(BaseModel):
    email: List[EmailStr]

async def send_email(email:EmailSchema,instance:User):
    token_data = {
        "id" : instance.id,
        "username": instance.username
    }

    token = jwt.encode(token_data,config_credentials["SECRET"],algorithm = 'HS256')

    template = f"""
        <!DOCTYPE html>
        <html>
            <head>
            
            </head>
            <body>
                <div style = "display:flex ;align-items:center;justify-content:center
                ;flex -direction:column"> 
                <h3> Email Verification</h3>
                <br>
                <p> Thank you for choosing us!!</p>
                <br>
                <p> Click on the button to verify your account</p>
                <a href = "http://localhost:8000/verification/?token={token}">
                Verify your account
                </a>
            </body>
        </html>
    """

    message = MessageSchema(
        subject = "Account Verification",
        recipients = email,
        body = "template",
        subtype = "html" 
    )

    fm = FastMail(conf)
    await fm.send_message(message) 
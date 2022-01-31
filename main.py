from fastapi import Depends, FastAPI,Request,status,HTTPException,WebSocket,Request
import pydantic
from tortoise.contrib.fastapi import register_tortoise
from authentication import (get_hashed_password, verify_token, token_generator)
from models import *
from tortoise.signals import post_save
from typing import List,Optional,Type
from tortoise import BaseDBAsyncClient
from fastapi.security import (OAuth2PasswordBearer,OAuth2PasswordRequestForm)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from emails import (send_email)

# sio: Any = socketio.AsyncServer(async_mode="asgi")
# socket_app = socketio.ASGIApp(sio)


app = FastAPI()
# app.mount("/", socket_app)

# @sio.on("connect")
# async def connect(sid, env):
#     print("Connected...")



# @sio.on("broadcast")
# async def broadcast(sid, msg):
#     print(f"broadcast {msg}")
#     await sio.emit("event_name", msg)  


# @sio.on("disconnect")
# async def disconnect(sid):
#     print("on disconnect")



outh2_schema = OAuth2PasswordBearer(tokenUrl='token')
@app.get("/")
async def home(request:Request):
    return templates.TemplateResponse("home.html",{"request":request})
    

async def get_current_user(token: str=Depends(outh2_schema)):
    try:
        payload =jwt.decode(token,config_credentials["SECRET"],algortihms=['HS256'] )
        user = await User.get(id = payload.get("id"))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid username or password",
            headers={'WWW-Authenticate':"Bearer"}
        )
    return await user

@app.post('/auth/login')
async def user_login(user:user_pydanticIn=Depends(get_current_user)):
    objects = await User.get(username = user.username)
    if objects is None :
        return {
            "status" :"404",
            "data":{
                "message" : "User not found.",
            }
        } 
    home()

@app.post('/token')
async def generate_token(request_form:OAuth2PasswordRequestForm = Depends()):
    token =  await token_generator(request_form.username ,request_form.password)
    return {"access_token": token, "token_type" :"bearer"}


@post_save(User)
async def checkuser(
    sender: "Type[User]",
    instance : User,
    created : bool,
    using_db : "Optional[BaseDBAsyncClient]",
    update_fields: List[str]
) ->None:
    if created:
        pass
        #await send_email([instance.email],instance)



@app.post("/registration")
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "status": "OK",
        "data" : f"Hello {new_user.username}. Thanks for registerting for our services. Please check your email for verification. "
    }


templates = Jinja2Templates(directory="templates")
@app.get("/verification", response_class=HTMLResponse)
async def acount_verification(request:Request,token:str):
    user = await verify_token(token)
    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse("verification.html",
        {"request":request,"username":user.username}) 


    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid token",
        headers = {"WWW-Authenticate": "Bearer"}
    )

websockets=[]
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()
	if websocket not in websockets:
		websockets.append(websocket)
	while True:
		data = await websocket.receive_text()
		for web in websockets:
			if web!=websocket:
				await web.send_text(f"{data}")




register_tortoise(
    app,
    db_url = "sqlite://database.sqlite3",
    modules = {"modes":["models"]},
    generate_schemas = True,
    add_exception_handlers = True
)
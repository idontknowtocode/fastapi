from email.policy import default
from tortoise import Model, fields
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk=True,index=True)
    username = fields.CharField(max_length= 20,null=False,unique=True)
    email = fields.CharField(max_length = 200,null=False,unique=True)
    password = fields.CharField(max_length= 200,null=False)
    join_date = fields.DatetimeField(default = datetime.utcnow),
    is_verified = fields.BooleanField(default=False)

user_pydantic = pydantic_model_creator(User,name ="User")
user_pydanticIn =  pydantic_model_creator(User, name = "UserIn",exclude_readonly = True,exclude=('is_verified','join_date'))
user_pydanticOut = pydantic_model_creator(User,name="UserOut",exclude =('password',))

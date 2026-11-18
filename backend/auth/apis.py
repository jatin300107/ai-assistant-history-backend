from fastapi import APIRouter , Depends , HTTPException
from sqlmodel import Session
from sqlmodel import Session
from backend.db import get_session
from .utlis import verify_register_details , create_password_hash , verify_login_details , create_jwt_token
from backend.models import User , Conversation , Message 
from pydantic import BaseModel



auth = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterUser(BaseModel):
    username: str
    password: str
    email: str
    


@auth.post('/register')
def register(user : RegisterUser, db : Session = Depends(get_session)):
    error = verify_register_details(user, db)
    if error is not None:
        return error
    hashed_password = create_password_hash(user.password)
   
    new_user = User(username = user.username , password = hashed_password , email=user.email )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully", "user_id": new_user.id}

class LoginUser(BaseModel):
    username : str
    password : str

@auth.post('/login')
def login(user : LoginUser , db : Session = Depends(get_session)):
    user_obj = verify_login_details(username = user.username, password=user.password ,db =  db)
    token = create_jwt_token(user_obj)
    return {"msg": "Login successful", "access_token": token}


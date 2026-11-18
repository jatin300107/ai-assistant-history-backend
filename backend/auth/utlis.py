from jose import jwt 
from fastapi import HTTPException  , Depends
from passlib.hash import bcrypt
from sqlmodel import Session, select
from backend.models import  User
from datetime import datetime , timedelta
import os
from dotenv import load_dotenv
from fastapi.security import HTTPBearer , HTTPAuthorizationCredentials
from backend.db import get_session
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
def verify_register_details(user,db : Session):
    existing = db.exec(select(User).where(User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400,detail="User already exists with this email")
    existing = db.exec(select(User).where(User.username==user.username)).first()
    if existing:
        raise HTTPException(status_code=400,detail="Username not available")
    return None

def create_password_hash(password : str):
    return bcrypt.hash(password)


    
def verify_password(plain_password,hashed_password):
    return bcrypt.verify(plain_password,hashed_password)

def verify_login_details(username,password, db : Session):
    existing = db.exec(select(User).where(User.username==username)).first()
    if not existing:
        raise HTTPException(status_code=400,detail="Invalid username or password")
    if not verify_password(password, existing.password):
        raise HTTPException(status_code=400,detail="Invalid username or password")
    return existing

def create_jwt_token(user : User):
    to_encode = {"user_id" : user.id , "username" : user.username }
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_session)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
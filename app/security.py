from datetime import timedelta, datetime
from fastapi import HTTPException, Depends
import jwt
from jose import jwt, JWTError
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_db
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from passlib.context import CryptContext
from app import models
from app.models import RoleEnum

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.Staff).filter(models.Staff.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(sub: str, roles: RoleEnum) -> str:
    return create_token(
        {"sub": sub, "role": roles, "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

def create_refresh_token(sub: str, roles: RoleEnum) -> str:
    return create_token(
        {"sub": sub, "role": roles, "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security), 
        db: Session = Depends(get_db)
    ):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
       raise credentials_exception
    
    user = db.query(models.Staff).filter(models.Staff.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(*required_roles: str):
    def role_checker(
        current_user: models.Staff = Depends(get_current_user)
    ):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    
    return role_checker
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from models import RoleEnum
from datetime import datetime

class StaffBase(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: RoleEnum = RoleEnum.staff

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[RoleEnum] = None

class StaffResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    created_at: datetime

    class Config:
        orm_mode = True

class StaffLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
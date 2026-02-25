from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class ScreeningCreate(BaseModel):
    job_description: str
    resume_text: str


class ScreeningResponse(BaseModel):
    id: int
    user_id: int
    job_description: str
    resume_text: str
    score: float
    feedback: str
    match_level: str
    created_at: datetime

    class Config:
        from_attributes = True

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v


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
    job_description: str = Field(..., min_length=10, max_length=10000)
    resume_text: str = Field(..., min_length=10, max_length=10000)


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

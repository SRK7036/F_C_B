from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class LeadCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    dob: date
    zip_code: str
    gender: Optional[str] = None
    address: str
    consent: bool = Field(True)

class LeadCreateResponse(BaseModel):
    session_token: str

class ChatRequest(BaseModel):
    session_token: str
    message: str

class ChatResponse(BaseModel):
    response: str

class AgreeRequest(BaseModel):
    session_token: str

class ExploreRequest(BaseModel):
    session_token: str
    preferences: str

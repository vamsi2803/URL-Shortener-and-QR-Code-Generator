from pydantic import BaseModel, HttpUrl, validator
from typing import Optional
from datetime import datetime

class URLBase(BaseModel):
    long_url: str
    custom_short_url: Optional[str] = None  
    expiration_date: Optional[datetime] = None
    @validator("long_url")
    def validate_long_url(cls, value):
        try:
            return str(HttpUrl(value))  
        except Exception:
            raise ValueError("Invalid URL: Provide a valid URL of the format http://www.example.com or https://www.example.com")

class ShortURLResponse(BaseModel):
    short_url: str
    qr_link: str

class LongURLResponse(BaseModel):
    long_url: str

"""
Database Schemas for Ješenca-Požeg Community Center

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name.

Collections used:
- Event -> "event"
- GalleryImage -> "galleryimage"
- ContactMessage -> "contactmessage"

Note: CenterInfo is a response model only (not stored as a collection).
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class Event(BaseModel):
    """Public events hosted at the community center"""
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    start: datetime = Field(..., description="Start datetime (ISO)")
    end: datetime = Field(..., description="End datetime (ISO)")
    all_day: bool = Field(False, description="Whether the event lasts all day")
    category: Optional[str] = Field(None, description="Category or tag for the event")


class GalleryImage(BaseModel):
    """Photo gallery images"""
    url: HttpUrl = Field(..., description="Public image URL")
    caption: Optional[str] = Field(None, description="Short caption for the image")
    credit: Optional[str] = Field(None, description="Photographer or source credit")


class ContactMessage(BaseModel):
    """Contact form submissions"""
    name: str = Field(..., description="Sender name")
    email: str = Field(..., description="Sender email")
    message: str = Field(..., min_length=5, max_length=2000, description="Message body")
    phone: Optional[str] = Field(None, description="Optional phone number")


# Response-only models (not collections)
class WeeklyHour(BaseModel):
    day: str
    open: str
    close: str
    note: Optional[str] = None


class CenterInfo(BaseModel):
    name: str
    address: str
    city: str
    country: str
    latitude: float
    longitude: float
    email: str
    phone: str
    website: Optional[str] = None
    schedule: List[WeeklyHour]

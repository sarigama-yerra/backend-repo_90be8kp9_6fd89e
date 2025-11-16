"""
Database Schemas for Bilal Qori – Trainer Soulful Qur’an Platform

Each Pydantic model below maps to a MongoDB collection (lowercased class name).
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone / WhatsApp number")
    role: str = Field("student", description="user | student | admin | partner")
    is_active: bool = Field(True)


class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str = Field(..., description="book | ebook | audio | video | merchandise | digital | equipment")
    image: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    rating: Optional[float] = Field(4.9, ge=0, le=5)


class OrderItem(BaseModel):
    product_id: str
    title: str
    qty: int = Field(..., ge=1)
    price: float = Field(..., ge=0)


class Order(BaseModel):
    user_email: EmailStr
    items: List[OrderItem]
    total: float = Field(..., ge=0)
    payment_status: str = Field("pending")
    checkout_session_id: Optional[str] = None


class Enrollment(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    program: str = Field(..., description="tilawah | workshop | webinar | membership")
    schedule: Optional[str] = Field(None, description="preferred time/event id")
    notes: Optional[str] = None


class Testimonial(BaseModel):
    name: str
    content: str
    avatar: Optional[str] = None
    platform: Optional[str] = Field("student")
    rating: Optional[int] = Field(5, ge=1, le=5)


class MediaItem(BaseModel):
    title: str
    type: str = Field(..., description="video | tutorial | reel | tiktok | instagram | youtube")
    url: str
    thumbnail: Optional[str] = None


class CommunityEvent(BaseModel):
    title: str
    date: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    gallery: Optional[List[str]] = None


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
    phone: Optional[str] = None

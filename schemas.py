from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    name: str = ""
    email: str
    password: str
    role: str = "buyer"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    class Config:
        from_attributes = True

class LotCreate(BaseModel):
    title: str
    price: int
    step: int
    seller_id: int

class LotUpdate(BaseModel):
    title: str
    price: int
    step: int

class LotResponse(BaseModel):
    id: int
    title: str
    price: int
    step: int
    seller_id: int
    class Config:
        from_attributes = True

class BidCreate(BaseModel):
    amount: int
    user_id: int

class NotificationResponse(BaseModel):
    id: int
    message: str
    class Config:
        from_attributes = True
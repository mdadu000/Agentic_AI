from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Restaurant Model
class Restaurant(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda dt: dt.isoformat()})
    
    # FIX: ID is now Optional. The Service will generate it.
    id: Optional[str] = None
    name: str
    location: str
    cuisine_type: str
    rating: Optional[float] = None
    created_at: Optional[datetime] = None

# MenuItem Model
class MenuItem(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda dt: dt.isoformat()})
    id: str
    restaurant_id: str
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None 
    
# Reservation Model
class Reservation(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda dt: dt.isoformat()})
    id: str
    restaurant_id: str
    user_id: str
    reservation_time: datetime
    guests: int

# Review Model
class Review(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda dt: dt.isoformat()})
    id: str
    restaurant_id: str
    user_id: str
    rating: float
    comment: Optional[str] = None
    timestamp: datetime
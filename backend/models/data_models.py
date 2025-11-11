from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Restaurant Model
class Restaurant(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda dt: dt.isoformat()})
    id: str
    name: str
    location: str
    cuisine_type: str
    rating: Optional[float] = None  # Rating is optional and can be a float

# MenuItem Model
class MenuItem(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda dt: dt.isoformat()})
    id: str
    restaurant_id: str  # Foreign Key to the Restaurant
    name: str
    description: Optional[str] = None
    price: float

# Reservation Model
class Reservation(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda dt: dt.isoformat()})
    id: str
    restaurant_id: str  # Foreign Key to the Restaurant
    user_id: str
    reservation_time: datetime
    guests: int

# List Models for API responses
class RestaurantListResponse(BaseModel):
    data: List[Restaurant]


class MenuItemListResponse(BaseModel):
    data: List[MenuItem]


class ReservationListResponse(BaseModel):
    data: List[Reservation]

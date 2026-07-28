from fastapi import APIRouter, status
from typing import List
from models.data_models import Restaurant, MenuItem, Reservation
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME

router = APIRouter()
repo = Repo(DB_NAME)
service = Service(repo)

# Create a new restaurant
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_restaurant(restaurant: Restaurant):
    """Create a new restaurant record"""
    return await service.create_restaurant(restaurant)

# Update an existing restaurant
@router.put("/{restaurant_id}", status_code=status.HTTP_200_OK)
async def update_restaurant(restaurant_id: str, restaurant: Restaurant):
    """Update an existing restaurant record"""
    return await service.update_restaurant(restaurant_id, restaurant)

# Delete a restaurant
@router.delete("/{restaurant_id}", status_code=status.HTTP_200_OK)
async def delete_restaurant(restaurant_id: str):
    """Delete a restaurant record"""
    return await service.delete_restaurant(restaurant_id)

# Get all restaurants
@router.get("/", response_model=List[Restaurant])
async def get_all_restaurants():
    """Retrieve all restaurants"""
    return await service.get_all_restaurants()

# Create a new menu item for a restaurant
@router.post("/{restaurant_id}/menu", status_code=status.HTTP_201_CREATED)
async def create_menu_item(restaurant_id: str, menu_item: MenuItem):
    """Create a new menu item for a restaurant"""
    menu_item.restaurant_id = restaurant_id  # Link menu item to the restaurant
    return await service.create_menu_item(menu_item)

# Update an existing menu item
@router.put("/menu/{menu_item_id}", status_code=status.HTTP_200_OK)
async def update_menu_item(menu_item_id: str, menu_item: MenuItem):
    """Update an existing menu item"""
    return await service.update_menu_item(menu_item_id, menu_item)

# Delete a menu item
@router.delete("/menu/{menu_item_id}", status_code=status.HTTP_200_OK)
async def delete_menu_item(menu_item_id: str):
    """Delete a menu item"""
    return await service.delete_menu_item(menu_item_id)

# Get all menu items for a restaurant
@router.get("/{restaurant_id}/menu", response_model=List[MenuItem])
async def get_menu_items(restaurant_id: str):
    """Retrieve all menu items for a given restaurant"""
    return await service.get_menu_items(restaurant_id)

# Create a new reservation for a restaurant
@router.post("/{restaurant_id}/reservations", status_code=status.HTTP_201_CREATED)
async def create_reservation(restaurant_id: str, reservation: Reservation):
    """Create a new reservation for a restaurant"""
    reservation.restaurant_id = restaurant_id  # Link reservation to the restaurant
    return await service.create_reservation(reservation)

# Update an existing reservation
@router.put("/reservations/{reservation_id}", status_code=status.HTTP_200_OK)
async def update_reservation(reservation_id: str, reservation: Reservation):
    """Update an existing reservation"""
    return await service.update_reservation(reservation_id, reservation)

# Delete a reservation
@router.delete("/reservations/{reservation_id}", status_code=status.HTTP_200_OK)
async def delete_reservation(reservation_id: str):
    """Delete a reservation"""
    return await service.delete_reservation(reservation_id)

# Get all reservations across all restaurants (All Bookings)
@router.get("/reservations/all", status_code=status.HTTP_200_OK)
async def get_all_reservations():
    """Retrieve all reservations and previous bookings across all restaurants"""
    return await service.get_all_reservations()

# Get all reservations for a restaurant
@router.get("/{restaurant_id}/reservations", response_model=List[Reservation])
async def get_reservations(restaurant_id: str):
    """Retrieve all reservations for a given restaurant"""
    return await service.get_reservations(restaurant_id)

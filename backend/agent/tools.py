import requests
from typing import Dict, List, Optional
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME
from models.data_models import MenuItem, Restaurant, Reservation, Review 
import uuid
from datetime import datetime

# Create repo and service instances
repo = Repo(DB_NAME)
service = Service(repo)

# --- HELPER FUNCTIONS ---
async def _get_restaurant_id_by_name(restaurant_name: str) -> Optional[str]:
    """Helper to find a restaurant's ID given its name."""
    all_restaurants = await service.get_all_restaurants()
    for restaurant in all_restaurants:
        if restaurant.name.lower() == restaurant_name.lower():
            return restaurant.id
    return None

def _generate_uuid():
    return str(uuid.uuid4())

# --- AGENT TOOLS (All Core & New Functionality) ---

# Core CRUD/List
async def get_all_restaurants() -> dict:
    """Retrieve all available restaurants."""
    restaurants = await service.get_all_restaurants()
    return {"restaurants": restaurants}

async def add_restaurant(name: str, location: str, cuisine_type: str, rating: Optional[float] = None) -> dict:
    """Adds a new restaurant to the database."""
    try:
        new_restaurant = Restaurant(id=_generate_uuid(), name=name, location=location, cuisine_type=cuisine_type, rating=rating)
        created = await service.create_restaurant(new_restaurant)
        return {"message": "Restaurant added successfully", "restaurant": created}
    except Exception as e:
        return {"error": f"Failed to add restaurant: {str(e)}"}

async def get_menu_items_for_restaurant(restaurant_name: str) -> dict:
    """Lists all menu items for a specific restaurant."""
    restaurant_id = await _get_restaurant_id_by_name(restaurant_name)
    if not restaurant_id: return {"error": f"Restaurant '{restaurant_name}' not found."}
    menu_items = await service.get_menu_items(restaurant_id)
    if not menu_items: return {"message": f"No menu items found for {restaurant_name}."}
    return {"restaurant": restaurant_name, "menu": menu_items}

async def add_menu_item(restaurant_name: str, item_name: str, price: float, description: Optional[str] = None, category: Optional[str] = None) -> dict:
    """Adds a new menu item to a specific restaurant."""
    restaurant_id = await _get_restaurant_id_by_name(restaurant_name)
    if not restaurant_id: return {"error": f"Restaurant '{restaurant_name}' not found."}
    try:
        new_item = MenuItem(id=_generate_uuid(), restaurant_id=restaurant_id, name=item_name, description=description, price=price, category=category)
        created = await service.create_menu_item(new_item)
        return {"message": "Menu item added successfully", "item": created}
    except Exception as e:
        return {"error": f"Failed to add menu item: {str(e)}"}

async def add_reservation(restaurant_name: str, user_id: str, reservation_time: str, guests: int) -> dict:
    """Creates a new reservation for a restaurant."""
    restaurant_id = await _get_restaurant_id_by_name(restaurant_name)
    if not restaurant_id: return {"error": f"Restaurant '{restaurant_name}' not found."}
    try:
        time_obj = datetime.fromisoformat(reservation_time)
        new_reservation = Reservation(id=_generate_uuid(), restaurant_id=restaurant_id, user_id=user_id, reservation_time=time_obj, guests=guests)
        created = await service.create_reservation(new_reservation)
        return {"message": "Reservation created successfully", "reservation": created}
    except Exception as e:
        return {"error": f"Failed to create reservation: {str(e)}"}
        
async def add_user_review(restaurant_name: str, user_id: str, rating: float, comment: Optional[str] = None) -> dict:
    """Implements user reviews: adds a new rating/review for a restaurant."""
    restaurant_id = await _get_restaurant_id_by_name(restaurant_name)
    if not restaurant_id: return {"error": f"Restaurant '{restaurant_name}' not found. Cannot add review."}
    try:
        new_review = Review(id=_generate_uuid(), restaurant_id=restaurant_id, user_id=user_id, rating=rating, comment=comment, timestamp=datetime.now())
        created = await service.create_review(new_review)
        return {"message": "Review added successfully", "review": created}
    except Exception as e:
        return {"error": f"Failed to add review: {str(e)}"}


# --- NEW UTILITY/ANALYTICS TOOLS ---

async def filter_restaurants_by_cuisine_tool(cuisine_type: str) -> dict:
    """Filter restaurants by a specific cuisine type (e.g., 'Italian', 'Mexican')."""
    try:
        restaurants = await service.filter_restaurants_by_cuisine(cuisine_type)
        if not restaurants: return {"message": f"No restaurants found for cuisine type '{cuisine_type}'."}
        return {"cuisine": cuisine_type, "restaurants": restaurants}
    except Exception as e:
        return {"error": f"Failed to filter restaurants: {str(e)}"}
        
async def search_for_menu_items_tool(item_name: str) -> dict:
    """Search for specific menu items across all restaurants by name."""
    try:
        items = await service.search_menu_items(item_name)
        if not items: return {"message": f"No menu items found matching '{item_name}'."}
        return {"search_term": item_name, "menu_items": items}
    except Exception as e:
        return {"error": f"Failed to search for menu items: {str(e)}"}

async def update_menu_item_price_tool(restaurant_name: str, item_name: str, new_price: float) -> dict:
    """Update the price of a specific menu item."""
    restaurant_id = await _get_restaurant_id_by_name(restaurant_name)
    if not restaurant_id: return {"error": f"Restaurant '{restaurant_name}' not found."}

    menu_items = await service.get_menu_items(restaurant_id)
    item_to_update = next((item for item in menu_items if item.name.lower() == item_name.lower()), None)
    
    if not item_to_update: return {"error": f"Item '{item_name}' not found at '{restaurant_name}'."}

    try:
        updated = await service.update_menu_item_price(item_to_update.id, new_price)
        if updated:
            return {"message": f"Price for '{item_name}' at '{restaurant_name}' updated successfully to {new_price}."}
        return {"message": f"Item ID {item_to_update.id} not found or price was already {new_price}."}
    except Exception as e:
        return {"error": f"Failed to update menu item price: {str(e)}"}

async def remove_restaurant_tool(restaurant_name: str) -> dict:
    """Remove a restaurant and all its associated data (menu items, reservations, reviews)."""
    restaurant_id = await _get_restaurant_id_by_name(restaurant_name)
    if not restaurant_id: return {"error": f"Restaurant '{restaurant_name}' not found."}
    try:
        deleted = await service.remove_restaurant(restaurant_id)
        if deleted:
            return {"message": f"Restaurant '{restaurant_name}' and all associated data successfully removed."}
        return {"message": f"Restaurant '{restaurant_name}' not found or already removed."}
    except Exception as e:
        return {"error": f"Failed to remove restaurant: {str(e)}"}
        
async def remove_menu_item_tool(restaurant_name: str, item_name: str) -> dict:
    """Removes a specific menu item from a restaurant."""
    restaurant_id = await _get_restaurant_id_by_name(restaurant_name)
    if not restaurant_id: return {"error": f"Restaurant '{restaurant_name}' not found."}

    menu_items = await service.get_menu_items(restaurant_id)
    item_to_delete = next((item for item in menu_items if item.name.lower() == item_name.lower()), None)

    if not item_to_delete:
        return {"message": f"Menu item '{item_name}' not found at '{restaurant_name}'."}

    try:
        deleted = await service.remove_menu_item(item_to_delete.id)
        if deleted:
            return {"message": f"Menu item '{item_name}' successfully deleted from '{restaurant_name}'."}
        return {"message": f"Failed to delete menu item '{item_name}'."}
    except Exception as e:
        return {"error": f"Failed to remove menu item: {str(e)}"}

async def get_reservations_today_tool() -> dict:
    """Calculate and list the number of reservations made for the current day."""
    try:
        reservations = await service.get_reservations_today()
        count = len(reservations)
        if not reservations: return {"message": "No reservations found for today.", "count": 0}
        return {"count": count, "reservations": reservations}
    except Exception as e:
        return {"error": f"Failed to get reservations for today: {str(e)}"}

async def get_all_reservations_tool() -> dict:
    """Retrieve all reservations and previous table bookings made across restaurants."""
    try:
        reservations = await service.get_all_reservations()
        count = len(reservations)
        if not reservations: return {"message": "No reservations or previous bookings found.", "count": 0}
        return {"count": count, "reservations": reservations}
    except Exception as e:
        return {"error": f"Failed to list all reservations: {str(e)}"}
        
async def get_highest_average_rating_restaurant() -> dict:
    """Identify the restaurant with the highest average rating based on user reviews."""
    try:
        restaurant = await service.get_highest_rated_restaurant()
        if not restaurant: return {"message": "No reviews or restaurants found to determine the highest rating."}
        return {"restaurant": restaurant}
    except Exception as e:
        return {"error": f"Failed to get highest rated restaurant: {str(e)}"}

async def get_best_rated_category_dish(category: str = 'Dessert') -> dict:
    """Determine which restaurant has the best-rated item in a specific menu category (e.q., 'Dessert')."""
    try:
        results = await service.get_best_rated_category(category)
        if not results: return {"message": f"No rated items found for the category '{category}'."}
        
        best_item = results[0]
        return {"category": category, "best_rated_item": best_item}
    except Exception as e:
        return {"error": f"Failed to get best rated item for category '{category}': {str(e)}"}
        
async def get_reservations_per_cuisine_type_tool() -> dict:
    """Access the number of reservations per cuisine type."""
    try:
        results = await service.get_reservations_per_cuisine()
        if not results: return {"message": "No reservations or cuisine types found."}
        return {"reservations_per_cuisine": results}
    except Exception as e:
        return {"error": f"Failed to get reservations per cuisine type: {str(e)}"}


# --- CHALLENGE ANALYTICS (Preserved) ---
async def get_most_recent_restaurant() -> dict:
    """Finds the restaurant that was added to the database most recently (Challenge)."""
    try:
        restaurant = await service.get_most_recent_restaurant()
        if not restaurant: return {"message": "No restaurants found."}
        return {"restaurant": restaurant}
    except Exception as e:
        return {"error": f"Failed to get most recent restaurant: {str(e)}"}

async def list_large_reservations(min_guests: int = 7) -> dict:
    """Lists all reservations with a guest count of min_guests or more (Challenge)."""
    try:
        reservations = await service.get_reservations_by_guest_count(min_guests)
        if not reservations: return {"message": f"No reservations found for {min_guests} or more guests."}
        return {"reservations": reservations}
    except Exception as e:
        return {"error": f"Failed to list large reservations: {str(e)}"}

async def get_restaurant_with_most_menu_items() -> dict:
    """Finds the restaurant that currently has the highest number of menu items (Challenge)."""
    try:
        restaurant = await service.get_restaurant_with_most_menu_items()
        if not restaurant: return {"message": "No restaurant or menu items found."}
        return {"restaurant": restaurant}
    except Exception as e:
        return {"error": f"Failed to find restaurant with most menu items: {str(e)}"}
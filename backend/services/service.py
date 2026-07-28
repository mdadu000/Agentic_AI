from typing import List, Optional, Dict
from models.data_models import Restaurant, MenuItem, Reservation, Review
from repos.repo import Repo
from datetime import datetime
import uuid
import collections


class Service:
    def __init__(self, repo: Repo):
        self.repo = repo
        
    # --- CORE CRUD ---
    async def create_restaurant(self, restaurant: Restaurant) -> Restaurant:
        await self.repo.init_db()
        if not restaurant.id: restaurant.id = str(uuid.uuid4())
        if not restaurant.created_at: restaurant.created_at = datetime.now() 
        await self.repo.insert_restaurant(restaurant)
        return restaurant
    
    async def get_all_restaurants(self) -> List[Restaurant]:
        await self.repo.init_db()
        return await self.repo.list_restaurants()

    async def get_menu_items(self, restaurant_id: str) -> List[MenuItem]:
        await self.repo.init_db()
        return await self.repo.list_menu_items(restaurant_id)
    
    async def create_menu_item(self, menu_item: MenuItem) -> MenuItem:
        await self.repo.init_db()
        if not menu_item.id: menu_item.id = str(uuid.uuid4())
        await self.repo.insert_menu_item(menu_item)
        return menu_item

    async def create_reservation(self, reservation: Reservation) -> Reservation:
        await self.repo.init_db()
        if not reservation.id: reservation.id = str(uuid.uuid4())
        await self.repo.insert_reservation(reservation)
        return reservation
        
    async def create_review(self, review: Review) -> Review:
        await self.repo.init_db()
        if not review.id: review.id = str(uuid.uuid4())
        if not review.timestamp: review.timestamp = datetime.now()
        await self.repo.insert_review(review)
        return review

    # --- ALL OTHER FUNCTIONALITIES ---
    async def filter_restaurants_by_cuisine(self, cuisine: str) -> List[Restaurant]:
        await self.repo.init_db()
        return await self.repo.list_restaurants_by_cuisine(cuisine)
        
    async def search_menu_items(self, item_name: str) -> List[MenuItem]:
        await self.repo.init_db()
        return await self.repo.list_menu_items_by_name(item_name)

    async def update_menu_item_price(self, item_id: str, new_price: float) -> bool:
        await self.repo.init_db()
        return await self.repo.update_menu_item_price(item_id, new_price)

    async def remove_restaurant(self, restaurant_id: str) -> bool:
        await self.repo.init_db()
        rows_deleted = await self.repo.delete_restaurant(restaurant_id)
        return rows_deleted > 0
        
    async def remove_menu_item(self, menu_item_id: str) -> bool:
        """Service wrapper to delete a menu item by ID."""
        await self.repo.init_db()
        rows_deleted = await self.repo.delete_menu_item(menu_item_id)
        return rows_deleted > 0
        
    async def get_reservations_today(self) -> List[Reservation]:
        await self.repo.init_db()
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time()).isoformat()
        end_of_day = datetime.combine(today, datetime.max.time()).isoformat()
        return await self.repo.list_reservations_today(start_of_day, end_of_day)

    async def get_all_reservations(self) -> List[Dict]:
        await self.repo.init_db()
        return await self.repo.list_all_reservations()

    async def delete_reservation(self, reservation_id: str) -> bool:
        await self.repo.init_db()
        return await self.repo.remove_reservation(reservation_id)

    async def get_highest_rated_restaurant(self) -> Optional[Restaurant]:
        await self.repo.init_db()
        avg_ratings = await self.repo.get_avg_ratings_by_restaurant()
        if not avg_ratings: return None
        
        highest_rated_id = avg_ratings[0]['restaurant_id']
        all_restaurants = await self.repo.list_restaurants()
        
        return next((r for r in all_restaurants if r.id == highest_rated_id), None)
        
    async def get_best_rated_category(self, category: str) -> List[Dict]:
        await self.repo.init_db()
        return await self.repo.get_best_rated_category_dish(category)
        
    async def get_reservations_per_cuisine(self) -> List[Dict]:
        await self.repo.init_db()
        return await self.repo.get_reservations_per_cuisine_type()
        
    # --- CHALLENGE ANALYTICS ---

    async def get_most_recent_restaurant(self) -> Optional[Restaurant]:
        await self.repo.init_db()
        all_restaurants = await self.repo.list_restaurants()
        if not all_restaurants: return None
        
        sorted_restaurants = sorted(
            all_restaurants, 
            key=lambda r: r.created_at if r.created_at else datetime.min, 
            reverse=True
        )
        return sorted_restaurants[0]

    async def get_reservations_by_guest_count(self, min_guests: int) -> List[Reservation]:
        await self.repo.init_db()
        return await self.repo.list_reservations_by_guests(min_guests)
        
    async def get_restaurant_with_most_menu_items(self) -> Optional[Restaurant]:
        await self.repo.init_db()
        
        all_menu_items = await self.repo.list_all_menu_items()
        if not all_menu_items: return None
            
        item_counts = collections.Counter(item.restaurant_id for item in all_menu_items)
        if not item_counts: return None

        most_items_id, _ = item_counts.most_common(1)[0]
        
        all_restaurants = await self.repo.list_restaurants()
        restaurant = next((r for r in all_restaurants if r.id == most_items_id), None)
        
        return restaurant
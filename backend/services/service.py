from typing import List
from fastapi import HTTPException
from models.data_models import Restaurant, MenuItem, Reservation
from repos.repo import Repo
from constants import MENU_ITEM_TABLE, RESERVATION_TABLE


class Service:
    def __init__(self, repo: Repo):
        self.repo = repo

    # Create a new restaurant
    async def create_restaurant(self, restaurant: Restaurant) -> Restaurant:
        await self.repo.init_db()
        if isinstance(restaurant, dict):
            restaurant = Restaurant(**restaurant)
        existing = await self.repo.get_restaurant(restaurant.id)
        if existing:
            raise HTTPException(
                status_code=409, detail="Restaurant already exists")
        await self.repo.insert_restaurant(restaurant)
        return restaurant

    # Get all restaurants
    async def get_all_restaurants(self) -> List[Restaurant]:
        await self.repo.init_db()
        return await self.repo.list_restaurants()

    # Update a restaurant's information
    async def update_restaurant(self, restaurant_id: str, restaurant: Restaurant) -> Restaurant:
        await self.repo.init_db()
        if isinstance(restaurant, dict):
            restaurant = Restaurant(**restaurant)
        restaurant.id = restaurant_id
        updated = await self.repo.update_restaurant(restaurant)
        if not updated:
            raise HTTPException(
                status_code=404, detail="Restaurant not found to update")
        return restaurant

    # Delete a restaurant
    async def delete_restaurant(self, restaurant_id: str):
        await self.repo.init_db()
        deleted_count = await self.repo.delete_restaurant(restaurant_id)
        if deleted_count == 0:
            raise HTTPException(
                status_code=404, detail="Restaurant not found to delete")
        return {"message": f"Restaurant with id {restaurant_id} deleted successfully"}

    # Create a new menu item
    async def create_menu_item(self, menu_item: MenuItem) -> MenuItem:
        await self.repo.init_db()
        if isinstance(menu_item, dict):
            menu_item = MenuItem(**menu_item)
        existing = await self.repo.get_menu_item(menu_item.id)
        if existing:
            raise HTTPException(
                status_code=409, detail="Menu item already exists")
        await self.repo.insert_menu_item(menu_item)
        return menu_item

    # Create a reservation
    async def create_reservation(self, reservation: Reservation) -> Reservation:
        await self.repo.init_db()
        if isinstance(reservation, dict):
            reservation = Reservation(**reservation)
        await self.repo.insert_reservation(reservation)
        return reservation

    # Get all menu items for a specific restaurant
    async def get_menu_items(self, restaurant_id: str) -> List[MenuItem]:
        await self.repo.init_db()
        return await self.repo.list_by_field(MENU_ITEM_TABLE, MenuItem, "restaurant_id", restaurant_id)

    # Get all reservations for a specific restaurant
    async def get_reservations(self, restaurant_id: str) -> List[Reservation]:
        await self.repo.init_db()
        return await self.repo.list_by_field(RESERVATION_TABLE, Reservation, "restaurant_id", restaurant_id)

    # Update a reservation
    async def update_reservation(self, reservation_id: str, reservation: Reservation) -> Reservation:
        await self.repo.init_db()
        if isinstance(reservation, dict):
            reservation = Reservation(**reservation)
        reservation.id = reservation_id
        updated = await self.repo.update_reservation(reservation)
        if not updated:
            raise HTTPException(
                status_code=404, detail="Reservation not found to update")
        return reservation

    # Delete a reservation
    async def delete_reservation(self, reservation_id: str):
        await self.repo.init_db()
        deleted_count = await self.repo.delete_reservation(reservation_id)
        if deleted_count == 0:
            raise HTTPException(
                status_code=404, detail="Reservation not found to delete")
        return {"message": f"Reservation with id {reservation_id} deleted successfully"}

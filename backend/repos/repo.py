import aiosqlite
from typing import List, Optional
from models.data_models import Restaurant, MenuItem, Reservation
from constants import DB_NAME, RESTAURANT_TABLE, MENU_ITEM_TABLE, RESERVATION_TABLE


class Repo:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path

    async def init_db(self):
        """Initialize tables if not exists."""
        async with aiosqlite.connect(self.db_path) as db:
            # Restaurant Table
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {RESTAURANT_TABLE} (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    cuisine_type TEXT NOT NULL,
                    rating REAL
                )
            """)
            # Menu Item Table
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {MENU_ITEM_TABLE} (
                    id TEXT PRIMARY KEY,
                    restaurant_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    FOREIGN KEY (restaurant_id) REFERENCES {RESTAURANT_TABLE}(id)
                )
            """)
            # Reservation Table
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {RESERVATION_TABLE} (
                    id TEXT PRIMARY KEY,
                    restaurant_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    reservation_time TEXT NOT NULL,
                    guests INTEGER NOT NULL,
                    FOREIGN KEY (restaurant_id) REFERENCES {RESTAURANT_TABLE}(id)
                )
            """)
            await db.commit()

    # Insert a new restaurant
    async def insert_restaurant(self, restaurant: Restaurant):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                INSERT INTO {RESTAURANT_TABLE} (id, name, location, cuisine_type, rating)
                VALUES (?, ?, ?, ?, ?)
            """, (
                restaurant.id,
                restaurant.name,
                restaurant.location,
                restaurant.cuisine_type,
                restaurant.rating
            ))
            await db.commit()

    # Insert a new menu item
    async def insert_menu_item(self, menu_item: MenuItem):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                INSERT INTO {MENU_ITEM_TABLE} (id, restaurant_id, name, description, price)
                VALUES (?, ?, ?, ?, ?)
            """, (
                menu_item.id,
                menu_item.restaurant_id,
                menu_item.name,
                menu_item.description,
                menu_item.price
            ))
            await db.commit()

    # Insert a new reservation
    async def insert_reservation(self, reservation: Reservation):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                INSERT INTO {RESERVATION_TABLE} (id, restaurant_id, user_id, reservation_time, guests)
                VALUES (?, ?, ?, ?, ?)
            """, (
                reservation.id,
                reservation.restaurant_id,
                reservation.user_id,
                reservation.reservation_time,
                reservation.guests
            ))
            await db.commit()

    # Get a restaurant by ID
    async def get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        query = f"""
            SELECT id, name, location, cuisine_type, rating
            FROM {RESTAURANT_TABLE} WHERE id = ?
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (restaurant_id,))
            row = await cursor.fetchone()
            if row:
                return Restaurant(
                    id=row[0],
                    name=row[1],
                    location=row[2],
                    cuisine_type=row[3],
                    rating=row[4]
                )
            return None

    # Get a menu item by ID
    async def get_menu_item(self, menu_item_id: str) -> Optional[MenuItem]:
        query = f"""
            SELECT id, restaurant_id, name, description, price
            FROM {MENU_ITEM_TABLE} WHERE id = ?
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (menu_item_id,))
            row = await cursor.fetchone()
            if row:
                return MenuItem(
                    id=row[0],
                    restaurant_id=row[1],
                    name=row[2],
                    description=row[3],
                    price=row[4]
                )
            return None

    async def list_restaurants(self) -> List[Restaurant]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                SELECT id, name, location, cuisine_type, rating
                FROM {RESTAURANT_TABLE}
            """)
            rows = await cursor.fetchall()
            return [
                Restaurant(
                    id=row[0],
                    name=row[1],
                    location=row[2],
                    cuisine_type=row[3],
                    rating=row[4]
                )
                for row in rows
            ]

    # Get all menu items for a restaurant
    async def list_menu_items(self, restaurant_id: str) -> List[MenuItem]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                SELECT id, restaurant_id, name, description, price
                FROM {MENU_ITEM_TABLE} WHERE restaurant_id = ?
            """, (restaurant_id,))
            rows = await cursor.fetchall()
            return [
                MenuItem(
                    id=row[0],
                    restaurant_id=row[1],
                    name=row[2],
                    description=row[3],
                    price=row[4]
                )
                for row in rows
            ]

    # Get all reservations for a restaurant
    async def list_reservations(self, restaurant_id: str) -> List[Reservation]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                SELECT id, restaurant_id, user_id, reservation_time, guests
                FROM {RESERVATION_TABLE} WHERE restaurant_id = ?
            """, (restaurant_id,))
            rows = await cursor.fetchall()
            return [
                Reservation(
                    id=row[0],
                    restaurant_id=row[1],
                    user_id=row[2],
                    reservation_time=row[3],
                    guests=row[4]
                )
                for row in rows
            ]

    # Delete a restaurant
    async def delete_restaurant(self, restaurant_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {RESTAURANT_TABLE} WHERE id = ?", (restaurant_id,))
            await db.commit()
            return cursor.rowcount

    # Delete a menu item
    async def delete_menu_item(self, menu_item_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {MENU_ITEM_TABLE} WHERE id = ?", (menu_item_id,))
            await db.commit()
            return cursor.rowcount

    # Delete a reservation
    async def delete_reservation(self, reservation_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {RESERVATION_TABLE} WHERE id = ?", (reservation_id,))
            await db.commit()
            return cursor.rowcount

    # Update a restaurant
    async def update_restaurant(self, restaurant: Restaurant) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                UPDATE {RESTAURANT_TABLE}
                SET name = ?, location = ?, cuisine_type = ?, rating = ?
                WHERE id = ?
            """, (
                restaurant.name,
                restaurant.location,
                restaurant.cuisine_type,
                restaurant.rating,
                restaurant.id
            ))
            await db.commit()
            return cursor.rowcount > 0

    # Update a menu item
    async def update_menu_item(self, menu_item: MenuItem) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                UPDATE {MENU_ITEM_TABLE}
                SET name = ?, description = ?, price = ?
                WHERE id = ?
            """, (
                menu_item.name,
                menu_item.description,
                menu_item.price,
                menu_item.id
            ))
            await db.commit()
            return cursor.rowcount > 0

    # Update a reservation
    async def update_reservation(self, reservation: Reservation) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                UPDATE {RESERVATION_TABLE}
                SET user_id = ?, reservation_time = ?, guests = ?
                WHERE id = ?
            """, (
                reservation.user_id,
                reservation.reservation_time,
                reservation.guests,
                reservation.id
            ))
            await db.commit()
            return cursor.rowcount > 0

    # Generic method to list records by a given field
    async def list_by_field(self, table_name: str, model_class, field_name: str, field_value: str):
        """Fetch all records from a specific table by a given field and map them to a model."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                SELECT * FROM {table_name}
                WHERE {field_name} = ?
            """, (field_value,))
            rows = await cursor.fetchall()

            # If no rows, return empty list
            if not rows:
                return []

            # Dynamically construct model objects
            columns = [col[0] for col in cursor.description]
            results = []
            for row in rows:
                data = dict(zip(columns, row))
                results.append(model_class(**data))

            return results

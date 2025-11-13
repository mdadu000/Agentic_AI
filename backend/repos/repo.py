import aiosqlite
from typing import List, Optional, Dict
from models.data_models import Restaurant, MenuItem, Reservation, Review 
from constants import DB_NAME, RESTAURANT_TABLE, MENU_ITEM_TABLE, RESERVATION_TABLE, REVIEW_TABLE
from datetime import datetime


class Repo:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path

    async def init_db(self):
        """Initializes tables, using ALTER TABLE to add missing columns without deleting data."""
        async with aiosqlite.connect(self.db_path) as db:
            
            async def check_and_add_column(table_name, column_name, column_type):
                cursor = await db.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not await cursor.fetchone(): return

                cursor = await db.execute(f"PRAGMA table_info({table_name})")
                cols = [col[1] for col in await cursor.fetchall()]
                if column_name not in cols:
                    await db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

            # 1. Restaurant Table
            await db.execute(f"CREATE TABLE IF NOT EXISTS {RESTAURANT_TABLE} (id TEXT PRIMARY KEY, name TEXT NOT NULL, location TEXT NOT NULL, cuisine_type TEXT NOT NULL, rating REAL)")
            await check_and_add_column(RESTAURANT_TABLE, "created_at", "TEXT") 
            
            # 2. Menu Item Table
            await db.execute(f"CREATE TABLE IF NOT EXISTS {MENU_ITEM_TABLE} (id TEXT PRIMARY KEY, restaurant_id TEXT NOT NULL, name TEXT NOT NULL, description TEXT, price REAL NOT NULL, FOREIGN KEY (restaurant_id) REFERENCES {RESTAURANT_TABLE}(id))")
            await check_and_add_column(MENU_ITEM_TABLE, "category", "TEXT")

            # 3. Reservation Table
            await db.execute(f"CREATE TABLE IF NOT EXISTS {RESERVATION_TABLE} (id TEXT PRIMARY KEY, restaurant_id TEXT NOT NULL, user_id TEXT NOT NULL, reservation_time TEXT NOT NULL, guests INTEGER NOT NULL, FOREIGN KEY (restaurant_id) REFERENCES {RESTAURANT_TABLE}(id))")
            
            # 4. Review Table
            await db.execute(f"CREATE TABLE IF NOT EXISTS {REVIEW_TABLE} (id TEXT PRIMARY KEY, restaurant_id TEXT NOT NULL, user_id TEXT NOT NULL, rating REAL NOT NULL, comment TEXT, timestamp TEXT NOT NULL, FOREIGN KEY (restaurant_id) REFERENCES {RESTAURANT_TABLE}(id))")

            await db.commit()

    # --- INSERTS ---
    async def insert_restaurant(self, restaurant: Restaurant):
        async with aiosqlite.connect(self.db_path) as db:
            created_at_str = restaurant.created_at.isoformat() if restaurant.created_at else datetime.now().isoformat()
            await db.execute(f"INSERT INTO {RESTAURANT_TABLE} (id, name, location, cuisine_type, rating, created_at) VALUES (?, ?, ?, ?, ?, ?)", 
                             (restaurant.id, restaurant.name, restaurant.location, restaurant.cuisine_type, restaurant.rating, created_at_str))
            await db.commit()

    async def insert_menu_item(self, menu_item: MenuItem):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"INSERT INTO {MENU_ITEM_TABLE} (id, restaurant_id, name, description, price, category) VALUES (?, ?, ?, ?, ?, ?)", 
                             (menu_item.id, menu_item.restaurant_id, menu_item.name, menu_item.description, menu_item.price, menu_item.category))
            await db.commit()
    
    async def insert_reservation(self, reservation: Reservation):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"INSERT INTO {RESERVATION_TABLE} (id, restaurant_id, user_id, reservation_time, guests) VALUES (?, ?, ?, ?, ?)", 
                             (reservation.id, reservation.restaurant_id, reservation.user_id, reservation.reservation_time.isoformat(), reservation.guests))
            await db.commit()
            
    async def insert_review(self, review: Review):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"INSERT INTO {REVIEW_TABLE} (id, restaurant_id, user_id, rating, comment, timestamp) VALUES (?, ?, ?, ?, ?, ?)", 
                             (review.id, review.restaurant_id, review.user_id, review.rating, review.comment, review.timestamp.isoformat()))
            await db.commit()

    # --- LISTS/GETS/ANALYTICS ---

    async def list_restaurants(self) -> List[Restaurant]:
        """FIXED: Selects all 6 columns explicitly and correctly converts created_at."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT id, name, location, cuisine_type, rating, created_at FROM {RESTAURANT_TABLE}")
            rows = await cursor.fetchall()
            
            restaurants = []
            for row in rows:
                created_at_dt = None
                if row[5]:
                     try: created_at_dt = datetime.fromisoformat(row[5])
                     except ValueError: pass 
                     
                restaurants.append(Restaurant(id=row[0], name=row[1], location=row[2], cuisine_type=row[3], rating=row[4], created_at=created_at_dt))
            return restaurants
            
    async def list_restaurants_by_cuisine(self, cuisine: str) -> List[Restaurant]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT id, name, location, cuisine_type, rating, created_at FROM {RESTAURANT_TABLE} WHERE cuisine_type LIKE ?", (f'%{cuisine}%',))
            rows = await cursor.fetchall()
            restaurants = []
            for row in rows:
                created_at_dt = None
                if row[5]:
                     try: created_at_dt = datetime.fromisoformat(row[5])
                     except ValueError: pass 
                restaurants.append(Restaurant(id=row[0], name=row[1], location=row[2], cuisine_type=row[3], rating=row[4], created_at=created_at_dt))
            return restaurants

    async def list_menu_items(self, restaurant_id: str) -> List[MenuItem]:
        """Fetches menu items for one restaurant, including category."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT id, restaurant_id, name, description, price, category FROM {MENU_ITEM_TABLE} WHERE restaurant_id = ?", (restaurant_id,))
            rows = await cursor.fetchall()
            return [MenuItem(id=row[0], restaurant_id=row[1], name=row[2], description=row[3], price=row[4], category=row[5]) for row in rows]

    async def list_menu_items_by_name(self, item_name: str) -> List[MenuItem]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT id, restaurant_id, name, description, price, category FROM {MENU_ITEM_TABLE} WHERE name LIKE ?", (f'%{item_name}%',))
            rows = await cursor.fetchall()
            return [MenuItem(id=row[0], restaurant_id=row[1], name=row[2], description=row[3], price=row[4], category=row[5]) for row in rows]
            
    async def list_all_menu_items(self) -> List[MenuItem]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT id, restaurant_id, name, description, price, category FROM {MENU_ITEM_TABLE}")
            rows = await cursor.fetchall()
            return [MenuItem(id=row[0], restaurant_id=row[1], name=row[2], description=row[3], price=row[4], category=row[5]) for row in rows]
            
    async def list_reservations_by_guests(self, min_guests: int) -> List[Reservation]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT id, restaurant_id, user_id, reservation_time, guests FROM {RESERVATION_TABLE} WHERE guests >= ?", (min_guests,))
            rows = await cursor.fetchall()
            return [Reservation(id=row[0], restaurant_id=row[1], user_id=row[2], reservation_time=datetime.fromisoformat(row[3]), guests=row[4]) for row in rows]
            
    async def list_reservations_today(self, start_of_day: str, end_of_day: str) -> List[Reservation]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT id, restaurant_id, user_id, reservation_time, guests FROM {RESERVATION_TABLE} WHERE reservation_time BETWEEN ? AND ?", (start_of_day, end_of_day))
            rows = await cursor.fetchall()
            return [Reservation(id=row[0], restaurant_id=row[1], user_id=row[2], reservation_time=datetime.fromisoformat(row[3]), guests=row[4]) for row in rows]

    async def get_avg_ratings_by_restaurant(self) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT restaurant_id, AVG(rating) AS average_rating FROM {REVIEW_TABLE} GROUP BY restaurant_id ORDER BY average_rating DESC")
            rows = await cursor.fetchall()
            return [{"restaurant_id": row[0], "average_rating": row[1]} for row in rows]
            
    async def get_best_rated_category_dish(self, category: str) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            query = f"""
                SELECT T1.id, T1.name, T1.restaurant_id, T2.rating 
                FROM {MENU_ITEM_TABLE} AS T1
                JOIN {REVIEW_TABLE} AS T2 ON T1.restaurant_id = T2.restaurant_id
                WHERE T1.category = ?
                ORDER BY T2.rating DESC
                LIMIT 10
            """
            cursor = await db.execute(query, (category,))
            rows = await cursor.fetchall()
            return [{"item_id": row[0], "item_name": row[1], "restaurant_id": row[2], "sample_rating": row[3]} for row in rows]

    async def get_reservations_per_cuisine_type(self) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            query = f"""
                SELECT T1.cuisine_type, COUNT(T2.id) AS reservation_count
                FROM {RESTAURANT_TABLE} AS T1
                JOIN {RESERVATION_TABLE} AS T2 ON T1.id = T2.restaurant_id
                GROUP BY T1.cuisine_type
                ORDER BY reservation_count DESC
            """
            cursor = await db.execute(query)
            rows = await cursor.fetchall()
            return [{"cuisine_type": row[0], "reservation_count": row[1]} for row in rows]
            
    # --- UPDATES ---
    async def update_menu_item_price(self, item_id: str, new_price: float) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"UPDATE {MENU_ITEM_TABLE} SET price = ? WHERE id = ?", (new_price, item_id))
            await db.commit()
            return cursor.rowcount > 0

    # --- DELETES ---
    async def delete_restaurant(self, restaurant_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"DELETE FROM {RESERVATION_TABLE} WHERE restaurant_id = ?", (restaurant_id,))
            await db.execute(f"DELETE FROM {MENU_ITEM_TABLE} WHERE restaurant_id = ?", (restaurant_id,))
            await db.execute(f"DELETE FROM {REVIEW_TABLE} WHERE restaurant_id = ?", (restaurant_id,))
            cursor = await db.execute(f"DELETE FROM {RESTAURANT_TABLE} WHERE id = ?", (restaurant_id,))
            await db.commit()
            return cursor.rowcount
            
    async def delete_menu_item(self, menu_item_id: str) -> int:
        """Deletes a single menu item by its ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {MENU_ITEM_TABLE} WHERE id = ?", (menu_item_id,))
            await db.commit()
            return cursor.rowcount
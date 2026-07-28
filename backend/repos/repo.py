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
            await self._seed_sample_dishes_if_needed(db)
            await db.commit()

    async def _seed_sample_dishes_if_needed(self, db):
        import uuid
        cursor = await db.execute(f"SELECT id, cuisine_type FROM {RESTAURANT_TABLE}")
        restaurants = await cursor.fetchall()
        
        sample_menus = {
            "indo-chinese": [
                ("Idli Manchurian", "Crispy fried rice cakes tossed in tangy Manchurian sauce & spring onions", 8.99, "Indo-Chinese"),
                ("Dosa 65", "Crispy crepe roll stuffed with spicy Andhra style cottage cheese & curry leaves", 9.99, "Indo-Chinese"),
                ("Hakka Vegetable Noodles", "Stir-fried wheat noodles with wok-tossed bell peppers & soy garlic", 11.50, "Noodles"),
                ("Schezwan Fried Rice", "Wok-tossed basmati rice with fiery Schezwan chili garlic paste", 10.99, "Main Course")
            ],
            "south-indian": [
                ("Masala Dosa", "Golden crispy rice crepe filled with spiced potato masala served with sambar", 8.50, "South Indian"),
                ("Steamed Rice Idli (3pcs)", "Fluffy steamed rice cakes served with coconut chutney & lentil sambar", 6.50, "South Indian"),
                ("Medu Vada (2pcs)", "Crispy fried lentil donuts seasoned with peppercorns & mint chutney", 6.99, "Starters"),
                ("Filter Coffee", "Traditional South Indian chicory decoction coffee brewed with hot milk", 3.50, "Beverages")
            ],
            "italian": [
                ("Margherita Basil Pizza", "Fresh mozzarella, vine tomatoes, organic basil & extra virgin olive oil", 14.99, "Main Course"),
                ("Truffle Cream Fettuccine", "Handmade fettuccine pasta in rich black truffle parmesan cream sauce", 18.50, "Main Course"),
                ("Classic Tiramisu", "Espresso-soaked ladyfingers with creamy mascarpone & cocoa powder", 8.99, "Dessert"),
                ("Crispy Garlic Bruschetta", "Toasted sourdough topped with diced heirloom tomatoes & fresh oregano", 7.50, "Starters")
            ],
            "indian": [
                ("Butter Chicken Masala", "Tender chicken cooked in rich creamy tomato butter sauce with authentic spices", 16.99, "Main Course"),
                ("Paneer Tikka Grill", "Marinated cottage cheese cubes grilled with bell peppers & mint chutney", 14.50, "Starters"),
                ("Garlic Butter Naan", "Freshly baked tandoori naan brushed with garlic butter & coriander", 4.25, "Breads"),
                ("Gulab Jamun with Ice Cream", "Warm milk dumplings served with vanilla bean ice cream", 6.99, "Dessert")
            ],
            "mexican": [
                ("Carne Asada Tacos (3pcs)", "Flame-grilled steak topped with cilantro, diced onions & salsa verde", 13.99, "Main Course"),
                ("Cheesy Nachos Supreme", "Tortilla chips layered with melted jack cheese, guacamole & jalapeños", 11.50, "Starters"),
                ("Chipotle Chicken Burrito", "Stuffed with seasoned rice, black beans, pico de gallo & grilled chicken", 14.25, "Main Course"),
                ("Churros with Chocolate Dip", "Cinnamon sugar crispy churros served with warm Mexican hot chocolate", 7.99, "Dessert")
            ],
            "default": [
                ("Classic Wagyu Burger", "Premium wagyu beef patty, cheddar, caramelized onions & secret sauce with fries", 17.50, "Main Course"),
                ("Crispy Caesar Salad", "Romaine hearts, parmesan crisp, garlic croutons & creamy Caesar dressing", 12.00, "Starters"),
                ("Molten Chocolate Lava Cake", "Warm chocolate cake with gooey molten center & fresh berries", 8.50, "Dessert"),
                ("Craft Lemonade Soda", "Freshly squeezed lemon juice with mint & sparkling water", 4.50, "Beverages")
            ]
        }

        for r_id, c_type in restaurants:
            c = await db.execute(f"SELECT COUNT(*) FROM {MENU_ITEM_TABLE} WHERE restaurant_id=?", (r_id,))
            count = (await c.fetchone())[0]
            if count == 0:
                c_key = "default"
                if c_type:
                    ct_lower = c_type.lower()
                    if "chinese" in ct_lower or "indo" in ct_lower: c_key = "indo-chinese"
                    elif "south" in ct_lower: c_key = "south-indian"
                    elif "italian" in ct_lower: c_key = "italian"
                    elif "indian" in ct_lower: c_key = "indian"
                    elif "mexican" in ct_lower: c_key = "mexican"

                dishes = sample_menus[c_key]
                for name, desc, price, cat in dishes:
                    item_id = str(uuid.uuid4())
                    await db.execute(
                        f"INSERT INTO {MENU_ITEM_TABLE} (id, restaurant_id, name, description, price, category) VALUES (?, ?, ?, ?, ?, ?)",
                        (item_id, r_id, name, desc, price, cat)
                    )

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

    async def list_all_reservations(self) -> List[Dict]:
        """Lists all reservations and previous bookings joined with restaurant names."""
        async with aiosqlite.connect(self.db_path) as db:
            query = f"""
                SELECT T1.id, T1.restaurant_id, T2.name AS restaurant_name, T1.user_id, T1.reservation_time, T1.guests
                FROM {RESERVATION_TABLE} AS T1
                LEFT JOIN {RESTAURANT_TABLE} AS T2 ON T1.restaurant_id = T2.id
                ORDER BY T1.reservation_time DESC
            """
            cursor = await db.execute(query)
            rows = await cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "restaurant_id": row[1],
                    "restaurant_name": row[2] or "Restaurant",
                    "user_id": row[3],
                    "reservation_time": row[4],
                    "guests": row[5]
                }
                for row in rows
            ]

    async def remove_reservation(self, reservation_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {RESERVATION_TABLE} WHERE id = ?", (reservation_id,))
            await db.commit()
            return cursor.rowcount > 0

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
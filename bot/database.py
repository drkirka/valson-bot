import aiosqlite
from bot.config import DB_PATH
from bot.matching import pair
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT NOT NULL DEFAULT 'ru'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY,
                gender TEXT NOT NULL,
                name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                height INTEGER NOT NULL,
                photo_file_id TEXT NOT NULL,
                description TEXT NOT NULL,
                contact TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                PRIMARY KEY(from_user_id,to_user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                a INTEGER NOT NULL,
                b INTEGER NOT NULL,
                PRIMARY KEY(a,b)
            )
        """)
        await db.commit()
async def set_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, language)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                language = excluded.language
        """, (user_id, language))
        await db.commit()
async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT language FROM users WHERE user_id = ?",(user_id,))
        row = await cursor.fetchone()
    return row[0] if row else "ru"
async def save_profile(user_id: int,gender: str,name: str,class_name: str,height: int,photo_file_id: str,description: str,contact: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO profiles (
                user_id, gender, name, class_name, height,
                photo_file_id, description, contact
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                gender = excluded.gender,
                name = excluded.name,
                class_name = excluded.class_name,
                height = excluded.height,
                photo_file_id = excluded.photo_file_id,
                description = excluded.description,
                contact = excluded.contact
        """, (user_id,gender,name,class_name,height,photo_file_id,description,contact))
        await db.commit()
async def delete_profile(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM likes WHERE from_user_id = ? OR to_user_id = ?", (user_id,user_id))
        await db.execute("DELETE FROM matches WHERE a = ? OR b = ?", (user_id,user_id))
        await db.commit()
async def get_profiles_by_class(class_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM profiles WHERE LOWER(class_name) = LOWER(?) ORDER BY name",(class_name,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
async def get_profile(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM profiles WHERE user_id = ?",(user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
async def add_like(from_user_id: int,to_user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO likes (from_user_id,to_user_id) VALUES (?,?)",(from_user_id,to_user_id))
        cursor = await db.execute("SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ?",(to_user_id,from_user_id))
        liked_back = await cursor.fetchone()
        if liked_back:
            a,b=pair(from_user_id,to_user_id)
            await db.execute("INSERT OR IGNORE INTO matches (a,b) VALUES (?,?)",(a,b))
        await db.commit()
        return bool(liked_back)
async def already_liked(from_user_id: int,to_user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ?",(from_user_id,to_user_id))
        return await cursor.fetchone() is not None

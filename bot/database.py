import aiosqlite
from bot.config import DB_PATH

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
                contact TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'both',
                experience TEXT NOT NULL DEFAULT '',
                availability TEXT NOT NULL DEFAULT '',
                tempo TEXT NOT NULL DEFAULT '',
                goals TEXT NOT NULL DEFAULT ''
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS prefs (
                user_id INTEGER PRIMARY KEY,
                preferred_class TEXT NOT NULL,
                preferred_role TEXT NOT NULL,
                min_height INTEGER NOT NULL,
                max_height INTEGER NOT NULL,
                experience TEXT NOT NULL,
                availability TEXT NOT NULL,
                tempo TEXT NOT NULL DEFAULT '',
                goals TEXT NOT NULL DEFAULT ''
            )
        """)
        for sql in [
            "ALTER TABLE profiles ADD COLUMN role TEXT NOT NULL DEFAULT 'both'",
            "ALTER TABLE profiles ADD COLUMN experience TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE profiles ADD COLUMN availability TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE profiles ADD COLUMN tempo TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE profiles ADD COLUMN goals TEXT NOT NULL DEFAULT ''",
        ]:
            try:
                await db.execute(sql)
            except aiosqlite.OperationalError:
                pass
        await db.commit()

async def set_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, language)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
        """, (user_id, language))
        await db.commit()

async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
    return row[0] if row else "ru"

async def save_profile(user_id:int, gender:str, name:str, class_name:str, height:int,
                       photo_file_id:str, description:str, contact:str,
                       role:str, experience:str, availability:str, tempo:str, goals:str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO profiles (
                user_id, gender, name, class_name, height, photo_file_id,
                description, contact, role, experience, availability, tempo, goals
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                gender=excluded.gender,
                name=excluded.name,
                class_name=excluded.class_name,
                height=excluded.height,
                photo_file_id=excluded.photo_file_id,
                description=excluded.description,
                contact=excluded.contact,
                role=excluded.role,
                experience=excluded.experience,
                availability=excluded.availability,
                tempo=excluded.tempo,
                goals=excluded.goals
        """, (user_id, gender, name, class_name, height, photo_file_id,
              description, contact, role, experience, availability, tempo, goals))
        await db.commit()

async def save_prefs(user_id:int, preferred_class:str, preferred_role:str,
                     min_height:int, max_height:int, experience:str,
                     availability:str, tempo:str, goals:str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO prefs (
                user_id, preferred_class, preferred_role, min_height, max_height,
                experience, availability, tempo, goals
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                preferred_class=excluded.preferred_class,
                preferred_role=excluded.preferred_role,
                min_height=excluded.min_height,
                max_height=excluded.max_height,
                experience=excluded.experience,
                availability=excluded.availability,
                tempo=excluded.tempo,
                goals=excluded.goals
        """, (user_id, preferred_class, preferred_role, min_height, max_height,
              experience, availability, tempo, goals))
        await db.commit()

async def delete_profile(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM prefs WHERE user_id = ?", (user_id,))
        await db.commit()

async def get_profiles_by_class(class_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM profiles WHERE LOWER(class_name) = LOWER(?) ORDER BY name",
            (class_name,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_profile(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_prefs(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM prefs WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_all_profiles():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM profiles ORDER BY name")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

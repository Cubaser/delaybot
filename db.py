from datetime import datetime

import aiosqlite

DB_NAME = 'messages.db'


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('PRAGMA journal_mode=WAL;')
        await db.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_forwards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_chat_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            send_at TEXT NOT NULL,
            sent INTEGER DEFAULT 0
        )
        """)
        await db.commit()


async def add_message(from_chat_id: int, message_id: int, send_at: datetime):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO scheduled_forwards (
                from_chat_id,
                message_id,
                send_at
            ) VALUES (?, ?, ?)
            """,
            (from_chat_id, message_id, send_at.isoformat()),
        )
        await db.commit()


async def get_pending_messages():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, from_chat_id, message_id, send_at
            FROM scheduled_forwards
            WHERE sent = 0
            """
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return rows


async def mark_as_sent(message_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE scheduled_forwards SET sent = 1 WHERE id = ?',
            (message_id,),
        )
        await db.commit()

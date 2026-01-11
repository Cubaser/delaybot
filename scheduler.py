import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from db import mark_as_sent

load_dotenv()

scheduler = AsyncIOScheduler()

TARGET_GROUP_ID = int(os.getenv('TARGET_GROUP_ID', 0))


def schedule_message(bot, msg_id, from_chat_id, message_id, send_at):
    scheduler.add_job(
        send_message,
        trigger='date',
        run_date=send_at,
        args=[bot, msg_id, from_chat_id, message_id],
        id=str(msg_id),
        replace_existing=True,
    )


async def send_message(bot, db_msg_id, from_chat_id, message_id):
    await bot.copy_message(
        chat_id=TARGET_GROUP_ID,
        from_chat_id=from_chat_id,
        message_id=message_id,
    )
    await mark_as_sent(db_msg_id)


async def load_jobs(bot, messages):
    for msg_id, from_chat_id, message_id, send_at in messages:
        schedule_message(
            bot,
            msg_id,
            from_chat_id,
            message_id,
            datetime.fromisoformat(send_at),
        )

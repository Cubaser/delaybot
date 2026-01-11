import asyncio
import os
import re
from datetime import datetime

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from apscheduler.jobstores.base import JobLookupError
from dotenv import load_dotenv

from db import add_message, get_pending_messages, init_db, mark_as_sent
from scheduler import load_jobs, schedule_message, scheduler

load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_waiting = {}


@dp.message(Command('start'))
async def start(message: types.Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        '🤖 Бот отложенных сообщений\n\n'
        '/add DD-MM-YYYY HH:MM - добавить отложенное сообщение\n'
        '/chatid - узнать chat_id\n'
        '/list - список запланированных сообщений\n'
        '/cancel_<ID> - отменить запланированное сообщение\n'
    )


@dp.message(Command('chatid'))
async def get_chat_id(message: types.Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        return
    await message.answer(f'Chat ID: {message.chat.id}')


@dp.message(Command('list'))
async def list_cmd(message: types.Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        return

    rows = await get_pending_messages()

    if not rows:
        await message.answer('📭 Нет запланированных сообщений')
        return

    text = '📋 Запланированные сообщения:\n\n'
    for task_id, message_id, send_at in rows:
        text += (
            f'🆔: {task_id}\n'
            f'🕒 {send_at}\n'
            f'📝 message_id: {message_id}\n'
            f'❌ Отменить: /cancel_{task_id}\n'
        )

    await message.answer(text)


@dp.message(F.text.regexp(r'^/cancel_(\d+)$'))
async def cancel_task(message: types.Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        return

    match = re.match(r'^/cancel_(\d+)$', message.text)
    msg_id = int(match.group(1))

    try:
        try:
            scheduler.remove_job(str(msg_id))
        except JobLookupError:
            pass
        await mark_as_sent(msg_id)
        await message.answer(f'❌ Сообщение {msg_id} отменено')
    except Exception:
        await message.answer('❌ Не удалось отменить сообщение')


@dp.message(Command('add'))
async def add(message: types.Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        return
    try:
        _, date, time = message.text.split()
        send_at = datetime.strptime(
            f'{date} {time}',
            '%d-%m-%Y %H:%M'
        )

        user_waiting[message.from_user.id] = {'send_at': send_at}
        await message.answer(
            '✅ Отлично! Отправь сообщение, которое нужно отправить в группу'
        )
    except Exception:
        await message.answer('❌ Формат команды: /add 15-01-2026 18:30')


@dp.message()
async def handle_forward(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_waiting:
        return

    info = user_waiting.pop(user_id)
    send_at = info['send_at']

    await add_message(
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        send_at=send_at,
    )

    pending = await get_pending_messages()
    last = pending[-1]

    schedule_message(bot, last[0], last[1], last[2], send_at)

    await message.answer(
        '✅ Сообщение запланировано и будет отправлено в группу'
    )


async def main():
    await init_db()

    pending = await get_pending_messages()
    await load_jobs(bot, pending)

    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

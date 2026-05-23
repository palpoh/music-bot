import asyncio
import os
import subprocess
import time
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

# 1. БЕРЕМ ТОКЕН ИЗ ОБЛАКА
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Ошибка: переменная окружения TOKEN не задана!")
ADMIN_IDS = [1973926980, 233188678]

# --- ЗАГЛУШКА ДЛЯ RENDER (Чтобы не падал из-за отсутствия порта) ---
async def handle(request):
    return web.Response(text="Бот жив")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
# -------------------------------------------------------------------

session = AiohttpSession(timeout=60)
bot = Bot(token=TOKEN, session=session, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

ROOT_DIR = os.getcwd()
last_bot_messages = {}

def get_project_file(user_id): return os.path.join(ROOT_DIR, f"current_project_{user_id}.tmp")

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Править", callback_data="edit_text"),
         InlineKeyboardButton(text="🔄 Другой момент", callback_data="reroll")],
        [InlineKeyboardButton(text="🎬 Собрать видео", callback_data="start_video")]
    ])

async def send_or_replace_message(message: Message, text: str, reply_markup=None, is_video=False, video_path=None):
    chat_id = message.chat.id
    if chat_id in last_bot_messages:
        try:
            await bot.delete_message(chat_id, last_bot_messages[chat_id])
        except: pass

    if is_video and video_path:
        msg = await bot.send_video(chat_id, video=FSInputFile(video_path), caption=text, reply_markup=reply_markup)
    else:
        msg = await bot.send_message(chat_id, text, reply_markup=reply_markup)
    last_bot_messages[chat_id] = msg.message_id
    return msg

@dp.message(F.text.startswith("ЭМИДАУН"))
async def generate_music(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("🚫 <b>У вас нет доступа.</b>")
        return

    prompt = message.text.replace("ЭМИДАУН", "").strip()
    if not prompt:
        await message.answer("⚠️ <b>Введите запрос</b>")
        return

    status_msg = await message.answer("🎵 <b>Запуск генерации...</b>")
    try:
        subprocess.run(["python3", "test_setup.py", prompt], check=True)
        if os.path.exists("final_fixed.wav"):
            await message.answer_audio(audio=FSInputFile("final_fixed.wav"), caption=f"🎵 <b>Бит:</b> {prompt}")
        else:
            await message.answer("❌ <b>Ошибка файла.</b>")
        await bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception as e:
        await message.answer(f"💥 <b>Ошибка:</b>\n<code>{e}</code>")

# ... (остальные функции handle_audio, process_project, callback-функции остаются без изменений) ...

async def main():
    # 2. ПРИНУДИТЕЛЬНЫЙ СБРОС СЕССИИ
    await bot.delete_webhook(drop_pending_updates=True)
    # 3. ЗАПУСК ВЕБ-СЕРВЕРА ДЛЯ RENDER
    await start_web_server()
    print("Бот и веб-сервер запущены!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

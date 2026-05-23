import asyncio
import os
import subprocess
import time
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

# БЕРЕМ ТОКЕН ИЗ ОБЛАКА
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Ошибка: переменная окружения TOKEN не задана!")
ADMIN_IDS = [1973926980, 233188678]

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
        except:
            pass

    if is_video and video_path:
        msg = await bot.send_video(chat_id, video=FSInputFile(video_path), caption=text, reply_markup=reply_markup)
    else:
        msg = await bot.send_message(chat_id, text, reply_markup=reply_markup)
    last_bot_messages[chat_id] = msg.message_id
    return msg


# --- ГЕНЕРАЦИЯ МУЗЫКИ (ТОЛЬКО ДЛЯ АДМИНОВ ПО ТЕГУ ЭМИДАУН) ---
@dp.message(F.text.startswith("ЭМИДАУН"))
async def generate_music(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("🚫 <b>У вас нет доступа к генерации.</b>")
        return

    prompt = message.text.replace("ЭМИДАУН", "").strip()
    if not prompt:
        await message.answer("⚠️ <b>Введите запрос после тега ЭМИДАУН</b>")
        return

    status_msg = await message.answer("🎵 <b>Запуск локальной генерации на M4...</b>")

    try:
        # Используем наш рабочий скрипт test_setup.py
        subprocess.run(["python3", "test_setup.py", prompt], check=True)

        if os.path.exists("final_fixed.wav"):
            await message.answer_audio(audio=FSInputFile("final_fixed.wav"), caption=f"🎵 <b>Бит:</b> {prompt}")
        else:
            await message.answer("❌ <b>Ошибка: файл final_fixed.wav не создан.</b>")

        await bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception as e:
        await message.answer(f"💥 <b>Ошибка генерации:</b>\n<code>{e}</code>")


@dp.message(F.audio | F.document)
async def handle_audio(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    document = message.audio or message.document
    project_id = f"project_{int(time.time())}"
    user_folder = os.path.join(ROOT_DIR, f"user_{message.from_user.id}")
    project_path = os.path.join(user_folder, project_id)
    os.makedirs(project_path, exist_ok=True)
    with open(get_project_file(message.from_user.id), "w") as f:
        f.write(project_path)

    msg = await message.answer("⏳ <b>Загрузка...</b>")
    try:
        await bot.download(document, destination=os.path.join(project_path, document.file_name))
        await process_project(message, project_path)
    except Exception as e:
        await message.answer(f"💥 <b>Ошибка:</b> {e}")


async def process_project(message: Message, project_path: str):
    subprocess.run(["python3", os.path.join(ROOT_DIR, "make_subs.py")], cwd=project_path)
    result_txt = os.path.join(project_path, "HOOK_READY.txt")
    mp3_path = os.path.join(project_path, "preview.mp3")
    if os.path.exists(result_txt):
        with open(result_txt, "r", encoding="utf-8") as f: content = f.read()
        await bot.send_voice(message.chat.id, FSInputFile(mp3_path))
        await send_or_replace_message(message, f"🎲 <b>Кусок готов:</b>\n<pre>{content}</pre>", get_main_kb())


@dp.callback_query(F.data == "reroll")
async def process_reroll(callback: CallbackQuery):
    with open(get_project_file(callback.from_user.id), "r") as f: project_path = f.read()
    await callback.message.delete()
    msg = await callback.message.answer("🔄 <b>Ищу другой момент...</b>")
    last_bot_messages[callback.message.chat.id] = msg.message_id
    await process_project(msg, project_path)
    await callback.answer()


@dp.callback_query(F.data == "start_video")
async def process_video_btn(callback: CallbackQuery):
    await callback.message.delete()
    msg = await callback.message.answer("🎬 <b>Рендерю видео, жди...</b>")
    with open(get_project_file(callback.from_user.id), "r") as f:
        project_path = f.read()
    subprocess.run(["python3", os.path.join(ROOT_DIR, "make_video.py")], cwd=project_path)
    video_file = os.path.join(project_path, "DRILL_PROMO_V7.mp4")
    if os.path.exists(video_file):
        await send_or_replace_message(msg, "Готово! 🔥", get_main_kb(), is_video=True, video_path=video_file)
    else:
        await msg.answer("❌ <b>Ошибка рендера.</b>")


@dp.callback_query(F.data == "edit_text")
async def process_edit_btn(callback: CallbackQuery):
    with open(get_project_file(callback.from_user.id), "r") as f: project_path = f.read()
    with open(os.path.join(project_path, "HOOK_READY.txt"), "r", encoding="utf-8") as f: content = f.read()
    await send_or_replace_message(callback.message, f"📝 <b>Исправь текст ниже:</b>\n<pre>{content}</pre>")
    await callback.answer()


@dp.message(F.text & F.reply_to_message)
async def save_and_render(message: Message):
    if "Исправь текст" not in message.reply_to_message.text: return
    with open(get_project_file(message.from_user.id), "r") as f: project_path = f.read()
    hook_file = os.path.join(project_path, "HOOK_READY.txt")
    with open(hook_file, "r", encoding="utf-8") as f: lines = f.readlines()
    with open(hook_file, "w", encoding="utf-8") as f:
        f.writelines(lines[:3])
        f.write(message.text)
    await send_or_replace_message(message, "✅ <b>Текст обновлен!</b>", get_main_kb())


async def main():
    # Эта строка отключает старые вебхуки и сбрасывает зависшие обновления
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__": asyncio.run(main())

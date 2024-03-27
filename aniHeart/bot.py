from curses import keyname
from curses.ascii import FS
from email import message
from importlib.resources import as_file
from select import kevent
from aiogram import Dispatcher, types, Bot, executor
import logging
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram import types
from data.settings import Setting
import re
from config import API_TOKEN
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,  ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, ContentTypes, Message, CallbackQuery
import sqlite3
from data.database_works import UserDatabase
from state.states import States
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

setting = Setting('data/setting.json')




# Replace 'YOUR_API_TOKEN' with your actual Telegram Bot API token


db = UserDatabase('database.db')
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())




# Echo handler
@dp.message_handler(commands=['start'])
async def echo(message: types.Message):
    
    keyboardButton = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Register', 'Login']

    keyboardButton.add(*buttons)

    await message.answer("Assalomu alaykom AniHeart.uz botiga hush kelibsiz😉.\n\n Bu yerdan siz o'zingizga kerakli bo'lgan animeni o'zbek tilida topishingiz mumkin bo'ladi🔍\n\nIltimos agar akkountingiz bo'lmasa ro'yhatdan o'ting", reply_markup=keyboardButton)

    


@dp.message_handler(lambda message: message.text == "Login")
async def login_form(message: Message):
    user_id = message.from_user.id



    if db.user_exists(user_id):
        await message.answer(f"Siz avval ham ro'yhatdan o'tgansiz")
    else:
        await message.answer(f"Iltimos ro'yhatdan o'ting")


user_data = {}


@dp.message_handler(lambda message: message.text == "Register")
async def register_form(message: Message, state: FSMContext):
    remove_keyboard = ReplyKeyboardRemove()
    
    await message.answer("Iltimos ismingizni kiritng", reply_markup=remove_keyboard)

    await state.set_state(States.name)


@dp.message_handler(state=States.name)
async def name(message: Message, state: FSMContext):
    user_data["name"] = message.text
    keyboardButton = ReplyKeyboardMarkup(resize_keyboard=True)



    contact_button = KeyboardButton("Raqamini yuborish" , request_contact=True)

    keyboardButton.add(contact_button)
    await message.answer("Iltimos telefon raqamingizni yuboring", reply_markup=keyboardButton)
    await state.finish()


@dp.message_handler(content_types=ContentTypes.CONTACT)
async def save_data(message: Message, state: FSMContext):
    username = user_data["name"]
    user_id = message.from_user.id
    number = message.contact.phone_number

    remove_keyboard = ReplyKeyboardRemove()

    db.insert_user(user_id, username, number)

    await message.answer("Welcome", reply_markup=remove_keyboard)



@dp.message_handler(commands=['admin'])
async def admin(message: Message):
    admin_id = message.from_user.id

    is_admin = db.admin_check(admin_id)

    if is_admin:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

        buttons = ["Janr qoshish", "Sozlamalar"]

        keyboard.add(*buttons)
        await message.answer("Welcome admin", reply_markup=keyboard)
    else:
        await message.answer("Ok")

    
@dp.message_handler(lambda message: message.text == "Janr qoshish")
async def add_genre(message: Message, state: FSMContext):
    admin_id = message.from_user.id
    is_admin = db.admin_check(admin_id)
    if is_admin:
        await message.answer("Iltimos janr nomini kiriting")
        await state.set_state(States.genre)


@dp.message_handler(state=States.genre)
async def genre_name(message: Message, state: FSMContext):
    admin_id = message.from_user.id
    genre_namex = message.text
    is_admin = db.admin_check(admin_id)

    if is_admin:
        db.insert_genere_name(genre_namex)
        await message.answer("Genre added")



# Function to handle message editing
async def edit_message(message: types.Message):
    if message.text:
        text = message.text.replace("/pub", "")
        if len(text) > 1:
            await bot.edit_message_text(
                text=text,
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Animeni ko'rish", url=f"{setting.data['myself']}?start={message.message_id}")]
                    ]
                )
            )
    elif message.caption:
        text = message.caption.replace("/pub", "")
        if len(text) > 1:
            await bot.edit_message_caption(
                caption=text,
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Animeni ko'rish", url=f"{setting.data['myself']}?start={message.message_id}")]
                    ]
                )
            )



pub = re.compile(r"/pub|.*/pub.*")

add_anime = re.compile(r"/add|.*/add.*")

vd_idx = {}

@dp.channel_post_handler(content_types=types.ContentTypes.TEXT)
async def catch_channel_text_message(message: types.Message):
    if pub.match(message.text):
        await edit_message(message)


@dp.channel_post_handler(content_types=types.ContentTypes.VIDEO)
async def catch_channel_video_message(message: types.Message):

    if message.caption and pub.match(message.caption):
        await edit_message(message)

    if message.caption and add_anime.match(message.caption):
        vd_idx.clear()

        vd_idx['anime_id'] = message.message_id
        await message.delete()

        # Fetch available genres
        genres = db.select_genres()

        keyboard = InlineKeyboardMarkup()

        for genre in genres:
            keyboard.add(InlineKeyboardButton(genre, callback_data=f"genre_{genre}"))
    
        # Prompt the user to select a genre
        await message.bot.send_message(message.chat.id, "Please select a genre for this anime:", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("genre_"))
async def add_anime_with_genre(callback: CallbackQuery):
    genre_names = callback.data.split("_")[1]

    add = db.insert_anme(genre_names)

    await callback.message.answer("Muvafaqiyatli qo'shildi")




# Handler for document messages
@dp.channel_post_handler(content_types=types.ContentTypes.DOCUMENT)
async def catch_channel_document_message(message: types.Message):
    if pub.match(message.text):
        await edit_message(message)


@dp.channel_post_handler(content_types=types.ContentTypes.PHOTO)
async def catch_channel_photo_message(message: types.Message):
    if message.caption and pub.match(message.caption):
        await edit_message(message)



if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    executor.start_polling(dp, skip_updates = False)

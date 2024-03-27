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

# Initialize database
db = UserDatabase('database.db')

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
channel_id = "-1001917113420"

# Regular expression pattern to match 'Name={name}'
name_pattern = re.compile(r'Name=([^\s]+)')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.get_args():
        anime_id = message.text.split(' ')[1].strip()
        anime_name = db.anime_name(anime_id)
        if anime_name:
            anime_idx = db.anime_id(anime_name)
            count = db.catch_anime_count(anime_name)

            keyboard = []
            buttons_per_row = 5
            for i in range(0, count, buttons_per_row):
                row = []
                for j in range(buttons_per_row):
                    index = i + j
                    if index < count:
                       
                        callback_data = f"anime_{anime_idx[index]}"
                        row.append(InlineKeyboardButton(f"{index + 1}", callback_data=callback_data))
                keyboard.append(row)
            keyboard.append([InlineKeyboardButton("♥", callback_data=f"love_{anime_name}")])


            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            await bot.copy_message(chat_id=message.chat.id,
                                    from_chat_id=channel_id,
                                    message_id=anime_id,
                                    reply_markup=reply_markup)
        else:
            await message.answer("Anime not found.")
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ['Register', 'Login']
        keyboard.add(*buttons)

        await message.answer("Assalomu alaykom AniHeart.uz botiga hush kelibsiz😉.\n\n Bu yerdan siz o'zingizga kerakli bo'lgan animeni o'zbek tilida topishingiz mumkin bo'ladi🔍\n\nIltimos agar akkountingiz bo'lmasa ro'yhatdan o'ting", reply_markup=keyboard)



@dp.callback_query_handler(lambda query: query.data.startswith("anime_"))
async def next_anime(query: CallbackQuery):
        await query.message.delete()
        anime_id = query.data.split("_")[1]
        
        anime_name = db.anime_name(anime_id)
        if anime_name:
            anime_idx = db.anime_id(anime_name)
            count = db.catch_anime_count(anime_name)

            keyboard = []
            buttons_per_row = 5
            for i in range(0, count, buttons_per_row):
                row = []
                for j in range(buttons_per_row):
                    index = i + j
                    if index < count:
                       
                        callback_data = f"anime_{anime_idx[index]}"
                        row.append(InlineKeyboardButton(f"{index + 1}", callback_data=callback_data))
                keyboard.append(row)

            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.copy_message(chat_id=query.message.chat.id,
                                        from_chat_id=channel_id,
                                        message_id=anime_id,
                                        reply_markup=reply_markup)


@dp.callback_query_handler(lambda query: query.data.startswith("love_"))
async def favorite(query: CallbackQuery):
    user_id = query.from_user.id
    anime_name = query.data.split("_")[1]

    db.add_anime_to_favorites(user_id, anime_name)

    await query.message.answer("Yoqtirishlarga qo'shildi")




@dp.message_handler(lambda message: message.text == "Login")
async def login_form(message: Message):
    user_id = message.from_user.id
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📔 Saqlanganlar", "Janr orqali qidirish🎥", "Nomi bo'yicha qidirish🔎"]
    keyboard.add(*buttons)
    if db.user_exists(user_id): 
        await message.answer(f"Hush kelibsiz", reply_markup=keyboard)
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
        await state.finish()


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
                            [types.InlineKeyboardButton(text="Animeni ko'rish", url=f"{setting.data['myself']}?start={message}")]
                        ]
                    )
                )
    elif message.caption:
        text = message.caption.replace("/pub", "")
        if len(text) > 1:
            match = name_pattern.search(message.caption)
            if match:
                name = match.group(1)
                anime_id = db.catch_anime_name(name)
                
                
                await bot.edit_message_caption(
                    caption=text,
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [types.InlineKeyboardButton(text="Animeni ko'rish", url=f"{setting.data['myself']}?start={anime_id[0]}")]
                        ]
                    )
                )


pub = re.compile(r"/pub|.*/pub.*")

add_anime = re.compile(r"/add|.*/add.*")

anime_info = {}

@dp.channel_post_handler(content_types=types.ContentTypes.TEXT)
async def catch_channel_text_message(message: types.Message):
    if pub.match(message.text):
        await edit_message(message)


@dp.channel_post_handler(content_types=types.ContentTypes.VIDEO)
async def catch_channel_video_message(message: types.Message):

    if message.caption and pub.match(message.caption):
        await edit_message(message)

    if message.caption and add_anime.match(message.caption):
        anime_info.clear()

        anime_info['anime_id'] = message.message_id

        # Remove '/add' from the caption
        cleaned_caption = message.caption.replace('/add', '').replace('=', ": ")
        await bot.edit_message_caption(chat_id=message.chat.id, caption=cleaned_caption, message_id=message.message_id)
        # Fetch available genres
        genres = db.select_genres()
        
        keyboard = InlineKeyboardMarkup()

        for genre in genres:
            keyboard.add(InlineKeyboardButton(genre, callback_data=f"genre_{genre}"))
    
                # Prompt the user to select a genre for this anime
        await message.bot.send_message(message.chat.id, "Please select a genre for this anime:", reply_markup=keyboard)
    
    match = name_pattern.search(message.caption)
    if match:
        # Extract the name from the matched group
        name = match.group(1)
        anime_info['anime_name'] = name


@dp.callback_query_handler(lambda query: query.data.startswith("genre_"))
async def add_anime_with_genre(callback: CallbackQuery):
    genre_names = callback.data.split("_")[1]
    await callback.message.delete()
    idx = anime_info["anime_id"]
    anime_name = anime_info["anime_name"]

    db.insert_anme(genre_names, anime_name, idx)

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




@dp.message_handler(lambda message: message.text == "Janr orqali qidirish🎥")
async def search_with_genre(message: Message):
    genres = db.select_genres()
        
    keyboard = InlineKeyboardMarkup()

    for genre in genres:
            keyboard.add(InlineKeyboardButton(genre, callback_data=f"searchgenre_{genre}"))
    
                # Prompt the user to select a genre for this anime
    await message.bot.send_message(message.chat.id, "Please select a genre for this anime:", reply_markup=keyboard)




@dp.callback_query_handler(lambda query: query.data.startswith("searchgenre_"))
async def search_genre(query: CallbackQuery):
    genre = query.data.split("_")[1]
   
    anime_names = db.catch_animename_by_genre(genre)
    print(anime_names)
    
    # Remove single-word entries
    anime_names = [anime_name for anime_name in anime_names if len(anime_name.split()) > 0]

    # Convert to set to ensure uniqueness
    anime_names_set = set(anime_names)

    # Convert back to sorted list
    anime_names = sorted(anime_names_set)

    print("Filtered and sorted anime names:", anime_names)
    
    if anime_names:
        anime_list = "\n".join([f"{index+1}. {anime_name}\n" for index, anime_name in enumerate(anime_names)])
        
        print("Constructed anime list:", anime_list)
        
        # Ensure anime_list is not empty before sending
        if anime_list.strip():  # Strip removes any leading/trailing whitespace
            keyboard = []
            buttons_per_row = 5
            index = len(anime_names)
            for i in range(0, index, buttons_per_row):
                row = []
                for j in range(buttons_per_row):
                    button_index = i + j
                    if button_index < index:
                        anime_name = anime_names[button_index]
                        callback_data = f"animebyGenre_{anime_name}"
                        row.append(InlineKeyboardButton(f"{button_index + 1}", callback_data=callback_data))
                keyboard.append(row)

            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            await query.message.answer(anime_list, reply_markup=reply_markup)
        else:
            print("Anime list is empty.")
            await query.message.answer("No anime found for this genre.")
    else:
        print("Filtered and sorted anime names are empty.")
        await query.message.answer("No anime found for this genre.")


@dp.callback_query_handler(lambda query: query.data.startswith("animebyGenre_"))
async def anime_from_genre(query: CallbackQuery):
        await query.message.delete()
        anime_name = query.data.split("_")[1]
        anime_id = db.anime_id(anime_name)

        
        print(anime_id)
        print(anime_name)
        if anime_name:
            anime_idx = db.anime_id(anime_name)
            count = db.catch_anime_count(anime_name)

            keyboard = []
            buttons_per_row = 5
            for i in range(0, count, buttons_per_row):
                row = []
                for j in range(buttons_per_row):
                    index = i + j
                    if index < count:
                       
                        callback_data = f"anime_{anime_idx[index]}"
                        row.append(InlineKeyboardButton(f"{index + 1}", callback_data=callback_data))
                keyboard.append(row)

            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.copy_message(chat_id=query.message.chat.id,
                                        from_chat_id=channel_id,
                                        message_id=anime_id[0],
                                        reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == "Nomi bo'yicha qidirish🔎")
async def search_by_name(message: Message, state: FSMContext):
    await message.answer("Iltimos anime nomini kiriting\nMisol uchun Naruto")

    await state.set_state(States.anime_name)
    

@dp.message_handler(state=States.anime_name)
async def founded_animes(message: Message, state: FSMContext):
    anime_name = message.text

    animes = db.search_by_name(anime_name)

    anime_list = "\n".join([f"{index+1}. {anime_name}\n" for index, anime_name in enumerate(animes)])
    
    keyboard = []
    buttons_per_row = 5
    index = len(animes)
    for i in range(0, index, buttons_per_row):
        row = []
        for j in range(buttons_per_row):
            button_index = i + j
            if button_index < index:
                anime_name = animes[button_index]
                print(anime_name)
                callback_data = f"animebyGenre_{anime_name}"
                row.append(InlineKeyboardButton(f"{button_index + 1}", callback_data=callback_data))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(anime_list, reply_markup=reply_markup)
    await state.finish()



@dp.message_handler(lambda message: message.text == "📔 Saqlanganlar")
async def saved_animes(message: Message):
    user_id = message.from_user.id
    saved = db.saved(user_id)
    anime_list = "\n".join([f"{index+1}. {anime_name}\n" for index, anime_name in enumerate(saved)])
    
    keyboard = []
    buttons_per_row = 5
    index = len(saved)
    for i in range(0, index, buttons_per_row):
        row = []
        for j in range(buttons_per_row):
            button_index = i + j
            if button_index < index:
                anime_name = saved[button_index]
                print(anime_name)
                callback_data = f"animebyGenre_{anime_name}"
                row.append(InlineKeyboardButton(f"{button_index + 1}", callback_data=callback_data))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(anime_list, reply_markup=reply_markup)






if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=False)

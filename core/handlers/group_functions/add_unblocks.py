from aiogram import types

from core.database_functions.db_functions import *


# this is admin function for adding lives for any user based on reply
async def add_unblocks_handler(message: types.Message, session):
    user_id = message.reply_to_message.from_user.id
    lives = int(message.text[14:]) if len(str(message.text)) >= 15 else 1
    await add_lives(user_id, session, lives)
    await message.delete()

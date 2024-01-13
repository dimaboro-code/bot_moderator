from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.models.data_models import AdminFunctions


add_unblock = InlineKeyboardButton(
    text='Добавить разблок',
    callback_data=AdminFunctions(function='add_unblock').pack()
)
remove_unblock = InlineKeyboardButton(
    text='Удалить 1 разблок',
    callback_data=AdminFunctions(function='remove_unblock').pack()
)
remove_all_unblocks = InlineKeyboardButton(
    text='Удалить все разблоки',
    callback_data=AdminFunctions(function='remove_all_unblocks').pack()
)


show_user_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [add_unblock],
    [remove_unblock],
    [remove_all_unblocks]
],
)

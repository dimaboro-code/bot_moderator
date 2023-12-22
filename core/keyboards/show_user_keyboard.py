from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

add_unblock = InlineKeyboardButton(
    text='Добавить разблок',
    callback_data='show_user_add_unblock'
)
remove_unblock = InlineKeyboardButton(
    text='Удалить 1 разблок',
    callback_data='show_user_remove_unblock'
)
remove_all_unblocks = InlineKeyboardButton(
    text='Удалить все разблоки',
    callback_data='show_user_remove_all_unblocks',

)


show_user_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [add_unblock],
    [remove_unblock],
    [remove_all_unblocks]
],
)

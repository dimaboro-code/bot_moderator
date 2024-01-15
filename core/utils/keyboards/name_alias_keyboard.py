from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.models.data_models import AdminFunctions


async def name_alias_keyboard(user_id: int, funcs: dict) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for button, func in funcs.items():
        builder.button(
            text=button,
            callback_data=AdminFunctions(function=func, user_id=user_id)
        )
    builder.adjust(1, repeat=True)
    return builder

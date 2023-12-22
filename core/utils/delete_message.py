# to use sleep() delays
import asyncio

# helper for delete_message()
from contextlib import suppress

# defines exceptions for delete_message()
from aiogram import types


async def delete_message(message: types.Message, delay_time: int = 0):

    # message removal after delay
    await asyncio.sleep(delay_time)

    # error handling, which avoide try-except block
    # handling exception messages.

    with suppress(Exception):
        await message.delete()

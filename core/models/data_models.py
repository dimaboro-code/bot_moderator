"""
Модели для данных
"""
from aiogram import types
from aiogram.filters.callback_data import CallbackData

from core.utils.get_username_from_text import is_username


class BaseData:
    """
    Базовый класс
    """

    def as_dict(self):
        """

        Returns: dict of class attrs

        """
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}


class UserData(BaseData):
    """
    Данные о пользователе
    userdata = UserData()
    userdata.parse_message(message)
    mute_data = userdata._dict
    """
    user_id: int | None
    username: str | None
    admin_id: int | None
    admin_username: str | None
    chat_id: int | None
    chat_username: str | None
    reason_message: str | None
    is_reply: bool | None

    def parse_message(self, message: types.Message, user_id: int | None = None):
        """
        Модель данных в виде интерфейса
        Args:
            message:
            user_id:
        Returns: self

        """
        if message.reply_to_message and user_id is None:
            self.user_id = message.reply_to_message.from_user.id
            self.username = message.reply_to_message.from_user.username
            self.admin_id = message.from_user.id
            self.admin_username = message.from_user.username
            self.chat_id = message.chat.id
            self.chat_username = message.chat.username
            self.reason_message = ' '.join(message.text.split()[1:])
            self.is_reply = True

        elif user_id:
            self.user_id = user_id
            self.username = is_username(message.text)
            self.admin_id = message.from_user.id
            self.admin_username = message.from_user.username
            self.chat_id = message.chat.id
            self.chat_username = message.chat.username
            self.reason_message = (' '.join(message.text.split()[2:]) if len(message.text.split()) <= 8
                                   else 'Ручной мьют, причину уточняйте у модератора')
            self.is_reply = False
        else:
            raise Exception
        return self

    @property
    def for_mute(self):
        data = {
            'user_id': self.user_id,
            'chat_id': self.chat_id,
            'moderator_message': self.reason_message,
            'admin_username': self.admin_username
        }
        return data


class AdminFunctions(CallbackData, prefix='show_user'):
    function: str
    user_id: int

"""
Модели для данных
"""
from aiogram import types
from aiogram.filters.callback_data import CallbackData

from core.utils.is_username import is_username


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

    def __init__(
        self,
        user_id: int | None = None,
        username: str | None = None,
        admin_id: int | None = None,
        admin_username: str | None = None,
        chat_id: int | None = None,
        chat_username: str | None = None,
        reason_message: str | None = None,
        is_reply: bool | None = None,
        *args,
        **kwargs
    ):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

        if args:
            print('too many args')

        self.user_id = user_id
        self.username = username
        self.admin_id = admin_id
        self.admin_username = admin_username
        self.chat_id = chat_id
        self.chat_username = chat_username
        self.reason_message = reason_message
        self.is_reply = is_reply
        self._dict = self.as_dict()

    def parse_message(self, message: types.Message, user_id: int | None = None):
        """
        Модель данных в виде интерфейса
        Args:
            message:
            user_id:
        Returns: self

        """
        if message.reply_to_message:
            self.user_id = message.reply_to_message.from_user.id
            self.username = message.reply_to_message.from_user.username
            self.admin_id = message.from_user.id
            self.admin_username = message.from_user.username
            self.chat_id = message.chat.id
            self.chat_username = message.chat.username
            self.reason_message = ' '.join(message.text.split()[1:])
            self.is_reply = True

        elif not message.reply_to_message:
            self.user_id = user_id
            self.username = is_username(message.text)
            self.admin_id = message.from_user.id
            self.admin_username = message.from_user.username
            self.chat_id = message.chat.id
            self.chat_username = message.chat.username
            self.reason_message = ' '.join(message.text.split()[2:])
            self.is_reply = False
        else:
            raise Exception

    @property
    def for_mute(self):
        data = {
            'user_id': self.user_id,
            'chat_id': self.chat_id,
            'message_id': 10,
            'moderator_message': self.reason_message,
            'admin_username': self.admin_username
        }
        return data


class AdminFunctions(CallbackData, prefix='show_user'):
    function: str
    user_id: int

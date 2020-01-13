import telebot
import os
import random

from datetime import datetime, timedelta
from time import sleep
from text_constants import WELCOME_MESSAGE, FLOOD_MESSAGES
from telegram_connector import bot


message_storage = []
chat_storage = []
chats_id = []
members_id = []


class ChatMember():
    def __init__(self, id):
        self._id = id
        self._message_history = []
        self._reverse_history = []
        self._short_message = 0
        self._is_not_short = 0

    def append_message(self, msg):
        self._message_history.append(msg)

    def get_id(self):
        return self._id

    def clear_message_history(self):
        self._message_history.clear()

    def check_message_length(self):
        self._reverse_history = list(reversed(self._message_history))

        if len(self._reverse_history) >= 4:
            for i in range(4):
                if len(self._reverse_history[i]) < 15:
                    self._short_message += 1

            if self._short_message == 4:
                self._short_message = 0
                self.clear_message_history()
                return True
            else:
                self._short_message = 0
                return False

    def check_for_clear_history(self):
        if len(self._reverse_history) >= 3:
            for i in range(3):
                if len(self._reverse_history[i]) >= 15:
                    self._is_not_short += 1

            if self._is_not_short == 3:
                self.clear_message_history()

            self._is_not_short = 0


class Chat():
    def __init__(self, id, counter):
        self._id = id
        self._message_counter = counter

    def get_id(self):
        return self._id

    def get_counter(self):
        return self._message_counter

    def set_counter(self, counter):
        self._message_counter = counter


def add_one_to_message_counter_in_chats(message):
    global chat_storage
    global chats_id

    if message.chat.id not in chats_id:
        chats_id.append(message.chat.id)
        chat_storage.append(Chat(message.chat.id, 0))

    for chat in chat_storage:
        if chat.get_id() == message.chat.id:
            chat.set_counter(chat.get_counter() + 1)
            break


@bot.message_handler(func=lambda message: True)
def count_all_messages(message):
    global message_storage
    global members_id

    add_one_to_message_counter_in_chats(message)

    if message.content_type == "text":
        if message.from_user.id not in members_id:
            members_id.append(message.from_user.id)
            message_storage.append(ChatMember(message.from_user.id))

        for chat_member in message_storage:
            if chat_member.get_id() == message.from_user.id:
                chat_member.append_message(message.text)
                if chat_member.check_message_length() is True:
                    bot.reply_to(message, FLOOD_MESSAGES[random.randint(0, 1)], parse_mode='HTML')
                    break


@bot.message_handler(content_types=["new_chat_members"])
def welcome_message(message):
    add_one_to_message_counter_in_chats(message)
    flag_counter = False

    for chat in chat_storage:
        if chat.get_id() == message.chat.id:
            if chat.get_counter() > 10:
                flag_counter = True
                chat.set_counter(0)

    if flag_counter:
        bot.send_message(message.chat.id, WELCOME_MESSAGE, parse_mode='HTML')


bot.polling(False, interval=0, timeout=20)

import os
import telebot

bot = telebot.TeleBot(os.environ.get('TELEGRAM_ACCESS_TOCKEN',
                                     'TOKEN'))

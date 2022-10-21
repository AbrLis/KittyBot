import logging
import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from pexel_module2 import send_pixel
from weather_module import send_weather

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_CAT = "https://api.thecatapi.com/v1/images/search"

logger_kitty = logging.getLogger(__name__)
logger_kitty.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger_kitty.addHandler(handler)

updater = Updater(token=TOKEN, use_context=True)


def say_hi(update, context):
    """Отвечает на приветствие"""
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text="Привет, я бот Котик")


def wake_up(update, context) -> None:
    """Просыпается и посылает случайного котика"""
    logger_kitty.info("Меня будят -)")
    chat = update.effective_chat
    button = ReplyKeyboardMarkup(
        [["/newcat", "/newfox", "/weather"]], resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat.id,
        text=f"Я проснулся {update.message.from_user.first_name},"
        f" Вот тебе новый котик",
        reply_markup=button,
    )
    send_cat(update, context)


def send_cat(update, context) -> None:
    """Отправляет случайного котика"""
    chat = update.effective_chat
    try:
        logger_kitty.info("Запрос нового котика")
        photo = requests.get(API_CAT).json()[0].get("url")
    except Exception as e:
        logger_kitty.error(f"Ошибка доступа к API котиков: {e}")
        context.bot.send_message(
            chat_id=chat.id, text="Сервис с котиками недоступен :("
        )
    else:
        logger_kitty.info("Отправка котика")
        context.bot.send_photo(chat_id=chat.id, photo=photo)


def main():
    """Инициализация бота"""
    updater.dispatcher.add_handler(CommandHandler("start", wake_up))
    updater.dispatcher.add_handler(CommandHandler("newcat", send_cat))
    updater.dispatcher.add_handler(CommandHandler("newfox", send_pixel))
    updater.dispatcher.add_handler(CommandHandler("weather", send_weather))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
    updater.start_polling()
    logger_kitty.info("Бот запущен")
    updater.idle()


if __name__ == "__main__":
    main()

# bot = Bot(token=TOKEN)
# text = 'Hello World!'
# bot.sendMessage(chat_id=CHAT_ID, text=text)

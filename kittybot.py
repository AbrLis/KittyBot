import os
import logging
import requests

# from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import ReplyKeyboardMarkup

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_CAT = "https://api.thecatapi.com/v1/images/search"

updater = Updater(token=TOKEN, use_context=True)


def say_hi(update, context):
    chat = update.effective_chat
    # message = update.message.text
    context.bot.send_message(chat_id=chat.id, text="Привет, я бот Котик")


def wake_up(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([["/newcat"]], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=f"Я проснулся {update.message.from_user.first_name},"
        f" Вот тебе новый котик",
        reply_markup=button,
    )
    send_cat(update, context)


def send_cat(update, context):
    chat = update.effective_chat
    try:
        photo = requests.get(API_CAT).json()[0].get("url")
    except Exception as e:
        logger.error(f"Ошибка доступа к API котиков: {e}")
        context.bot.send_message(
            chat_id=chat.id, text="Сервис с котиками недоступен :("
        )
    else:
        context.bot.send_photo(chat_id=chat.id, photo=photo)


def main():
    updater.dispatcher.add_handler(CommandHandler("start", wake_up))
    updater.dispatcher.add_handler(CommandHandler("newcat", send_cat))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
    updater.start_polling()
    logger.info("Бот запущен")
    updater.idle()


if __name__ == "__main__":
    main()

# bot = Bot(token=TOKEN)
# text = 'Hello World!'
# bot.sendMessage(chat_id=CHAT_ID, text=text)

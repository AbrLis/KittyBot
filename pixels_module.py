import json
import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()
API_PEXELS = os.getenv("API_PIXELS")
API_PEXELS_URL = "https://api.pexels.com/v1/search"
headers = {
    "Authorization": API_PEXELS,
}

logger_pexel = logging.getLogger(__name__)
logger_pexel.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger_pexel.addHandler(handler)

file_ulr = "./file/page_fox.json"
try:
    with open(file_ulr, "r") as f:
        page = json.load(f)
except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
    logger_pexel.error(f"Файл не найден, начинаем с первой страницы {e}")
    page = {}


def save_page():
    """Сохранение страницы"""
    # Так как страницы статичны, то приходится их сохранить дабы не было
    # повторов
    try:
        with open(file_ulr, "w") as f:
            json.dump(page, f)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        logger_pexel.error(f"Ошибка сохранения страницы: {e}")


def get_first_page() -> None:
    """Получение первой страницы"""
    global page
    params = {
        "query": "fox",
        "per_page": 1,
    }
    try:
        response = requests.get(
            API_PEXELS_URL,
            params=params,
            headers=headers,
        ).json()
    except Exception as e:
        logger_pexel.error(f"Ошибка доступа к API pixels: {e}")
        page = {}
    else:
        page = response
        save_page()


def get_pexel_page() -> str:
    """Получение следующей страницы"""
    global page
    if not page or not page.get("next_page"):
        get_first_page()
        if not page:
            logging.error("Не удалось получить первую страницу")
            return "Не удалось получить страницу"
    else:
        try:
            page = requests.get(page["next_page"], headers=headers).json()
            save_page()
        except Exception as e:
            logger_pexel.error(f"Ошибка доступа к API pixels: {e}")
            page = {}
            return "Не удалось получить страницу"


def send_pixel(update, context) -> None:
    """Отправляет следующую картинку"""
    err = get_pexel_page()
    chat = update.effective_chat
    if err:
        context.bot.send_message(chat_id=update.chat.id, text=err)
        return
    try:
        logger_pexel.info("Запрос нового фото")
        photo = page["photos"][0]["src"]["large"]
        alt = page["photos"][0]["alt"]
    except Exception as e:
        logger_pexel.error(f"Ошибка получения фото: {e}")
        context.bot.send_message(
            chat_id=chat.id, text="Ошибка получения фото :("
        )
    else:
        logger_pexel.info(f"Отправка фото номер: {page.get('page')}")
        context.bot.send_photo(chat_id=chat.id, photo=photo, caption=alt)

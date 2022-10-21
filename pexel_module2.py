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
file_path = "./file/page_fox.json"

logger_pexel = logging.getLogger(__name__)
logger_pexel.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger_pexel.addHandler(handler)


# Загрузка страницы
data_page = {}
try:
    logger_pexel.info("Загрузка данных")
    with open(file_path, "r") as f:
        data_page = json.load(f)
except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
    logger_pexel.critical(f"Файл не найден, начинаем с первой страницы {e}")
    data_page = {}


def save_page():
    """Сохранение данных по пользователям"""
    try:
        logger_pexel.info("Сохраниение данных")
        with open(file_path, "w") as f:
            json.dump(data_page, f)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        logger_pexel.error(f"Ошибка сохранения страницы: {e}")


def get_page(chat_id) -> dict:
    """Получение страницы"""
    params = {
        "query": "fox",
        "per_page": 1,
        "page": 1,
    }
    if chat_id in data_page:
        try:
            max_picture = data_page[chat_id]["total_results"]
            params["page"] = (
                data_page[chat_id]["page"] + 1
                if data_page[chat_id]["page"] < max_picture
                else 1
            )
        except Exception as e:
            logger_pexel.error(f"Ошибка получения страницы: {e}")
            params["page"] = 1
    try:
        logger_pexel.info("Запрос к API новой картинки")
        response = requests.get(
            API_PEXELS_URL,
            params=params,
            headers=headers,
        ).json()
    except Exception as e:
        logger_pexel.error(f"Ошибка доступа к API pixels: {e}")
        return {"error": "Не смог получить картинку :("}
    return response


def send_pixel(update, context) -> None:
    """Отправляет следующую картинку"""
    global data_page
    chat_id = str(update.effective_chat.id)
    response = get_page(chat_id)
    if 'error' in response:
        context.bot.send_message(chat_id=chat_id, text=response['error'])
        return
    logger_pexel.info("Успешный запрос картики")
    total_results = response.get("total_results")
    if total_results and total_results == 0:
        context.bot.send_message(
            chat_id=int(chat_id), text="Картинок больше нет"
        )
        return
    data_page[chat_id] = response
    try:
        logger_pexel.info("Отправка фото")
        context.bot.send_photo(
            chat_id=int(chat_id),
            photo=response["photos"][0]["src"]["large"],
            caption=response["photos"][0]["alt"],
        )
    except Exception as e:
        logger_pexel.error(f"Ошибка отправки фото: {e}")
        context.bot.send_message(
            chat_id=int(chat_id), text="Не смог отправить картинку :("
        )
    else:
        logger_pexel.info("Отправка картиночки прошла успешно")
        save_page()

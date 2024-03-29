import logging
import os
import random
import time

import requests
from dotenv import load_dotenv

load_dotenv()
API_PEXELS = os.getenv("API_PIXELS")
API_PEXELS_URL = "https://api.pexels.com/v1/search"
DAY_IN_SECONDS = 24 * 60 * 60

headers = {
    "Authorization": API_PEXELS,
}
params = {
    "query": "animals",
    "per_page": 1,
    "page": 1,
}
total_results = {}
new_search = False

logger_pexel = logging.getLogger(__name__)
logger_pexel.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger_pexel.addHandler(handler)


def get_pexel(page=1) -> dict:
    """Получение запрошеной страницы"""
    params["page"] = page
    try:
        logger_pexel.info("Запрос страницы картинок с Pexels")
        response = requests.get(
            API_PEXELS_URL,
            params=params,
            headers=headers,
            timeout=5,
        ).json()
    except Exception as e:
        logger_pexel.error(f"Ошибка запроса: {e}")
        return {"error": "Не смог получить данные от сервера картиночек :("}
    logger_pexel.info("Получен ответ от сервера")
    return response


def get_page(chat_id) -> dict:
    """Получение страницы"""
    global new_search
    time_now = time.time()
    diff_time = (
        time_now - total_results["date"]
        if total_results.get("date")
        else time_now
    )
    # Запрос максимального числа картинок
    # если с последнего запроса прошло больше суток
    # или это новый поиск
    if new_search or not total_results or diff_time > DAY_IN_SECONDS:
        logger_pexel.info("Запрос максимального числа картинок")
        response = get_pexel()
        if "error" in response:
            return response
        total_results["date"] = time.time()
        if response["total_results"] == 0:
            return {
                "error": "Не смог найти картинок по вашему запросу :(\n "
                "Введите запрос на английском языке"
            }
        new_search = False
        total_results["total_results"] = response.get("total_results")
    # Запрос случайной картинки из всего списка
    page = random.randint(1, total_results["total_results"])
    logger_pexel.info(f"Запрос случайной картинки {page}")
    return get_pexel(page)


def send_pixel(update, context) -> None:
    """Отправляет следующую картинку"""
    global new_search
    chat_id = str(update.effective_chat.id)
    search = update.message.text.split(" ", 1)
    if len(search) > 1 and isinstance(search[1], str):
        params["query"] = search[1]
        new_search = True
    response = get_page(chat_id)
    if "error" in response:
        context.bot.send_message(chat_id=chat_id, text=response["error"])
        return
    try:
        logger_pexel.info("Отправка фото")
        context.bot.send_photo(
            chat_id=int(chat_id),
            photo=response["photos"][0]["src"]["large2x"],
            caption=(
                f'Всего найдено картинок: {total_results["total_results"]}\n'
                f'Текущая картинка: {params["page"]}\n'
                f'{response["photos"][0]["alt"]}'
            ),
        )
    except Exception as e:
        logger_pexel.error(f"Ошибка отправки фото: {e}")
        context.bot.send_message(
            chat_id=int(chat_id), text="Не смог отправить картинку :("
        )
    else:
        logger_pexel.info("Отправка картиночки прошла успешно")

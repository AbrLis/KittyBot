import os
import logging
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv


load_dotenv()

API_WEATHER = os.getenv("API_WEATHER")
API_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_ICONS = {
    "01d": "☀️",
    "01n": "🌙",
    "02d": "⛅️",
    "02n": "⛅️",
    "03d": "☁️",
    "03n": "☁️",
    "04d": "☁️",
    "04n": "☁️",
    "09d": "🌧",
    "09n": "🌧",
    "10d": "🌦",
    "10n": "🌦",
    "11d": "⛈",
    "11n": "⛈",
    "13d": "❄️",
    "13n": "❄️",
    "50d": "🌫",
    "50n": "🌫",
}

logger_weather = logging.getLogger(__name__)
logger_weather.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger_weather.addHandler(handler)

weather_dict = {}


def get_wind_direction(degrees):
    """Возвращает направление ветра"""
    if degrees < 22.5:
        return "северный"
    if degrees < 67.5:
        return "северо-восточный"
    if degrees < 112.5:
        return "восточный"
    if degrees < 157.5:
        return "юго-восточный"
    if degrees < 202.5:
        return "южный"
    if degrees < 247.5:
        return "юго-западный"
    if degrees < 292.5:
        return "западный"
    if degrees < 337.5:
        return "северо-западный"
    return "северный"


def get_time(unixtime, tz) -> str:
    """Возвращает время в формате HH:MM:SS c учетом часового пояса"""
    if not tz:
        return "нет данных"
    tz = timezone(+timedelta(seconds=tz))
    return datetime.fromtimestamp(unixtime, tz).strftime("%H:%M:%S")


def parse_weather(result):
    """Получает погоду из ответа API"""
    try:
        logger_weather.info(f"Парсинг погоды {result}")
        city = result.get("name")
        conditions = result.get("weather")[0].get("description")
        temp = int(result.get("main").get("temp"))
        temp_feels_like = int(result.get("main").get("feels_like"))
        wind = result["wind"]["speed"]
        wind_gust = result.get("wind").get("gust") or "нет данных"
        wind_direction = get_wind_direction(result["wind"]["deg"])
        icon = WEATHER_ICONS.get(result["weather"][0]["icon"])
        visibility = result["visibility"] / 1000
        tz = result.get("timezone")
        sunraise = get_time(result["sys"]["sunrise"], tz)
        sunset = get_time(result["sys"]["sunset"], tz)
        logger_weather.info("Парсинг погоды завершен успешно")
        return (
            f"Погода в городе {city}: {conditions} {icon}\n "
            f"🌡Температура {temp}°C, Ощущается как {temp_feels_like}°C\n"
            f"Средняя видимость: {visibility} км\n"
            f"Направление ветра: {wind_direction}\n"
            f"💨 {wind} м/с, порывами до 💨 {wind_gust} м/с\n"
            f"🌅Восход: {sunraise}, 🌇Закат: {sunset}"
        )
    except Exception as e:
        logger_weather.error(f"Ошибка обработки ответа API погоды: {e}")
        return "Извините, произошла ошибка, неожиданный ответ сервиса"


def get_weather(city) -> str:
    """Получает погоду в заданном городе"""
    try:
        logger_weather.info(f"Запрос погоды для города {city}")
        result = requests.get(
            API_WEATHER_URL,
            params={
                "q": city,
                "units": "metric",
                "lang": "ru",
                "APPID": API_WEATHER,
            },
        ).json()
        if result.get("cod") != 200:
            logger_weather.info(
                f"Ошибка получения погоды: {result.get('message')}"
            )
            return result.get("message")
        logger_weather.info(f"Погода в городе: {city} - Получена успешно")
        return parse_weather(result)
    except Exception as e:
        logger_weather.error(f"Ошибка получения погоды: {e}")
        return "Сервис погоды временно недоступен :("


def send_weather(update, context) -> None:
    """Отправляет погоду в заданном городе"""
    chat = update.effective_chat
    city = update.message.text.replace("/weather", "")
    if city and isinstance(city, str):
        weather_dict[chat.id] = city.strip()
    if chat.id in weather_dict:
        city = weather_dict.get(chat.id)
        # Запрос к api погоды
        message = get_weather(city)
    else:
        message = (
            "Я пока не знаю в каком городе ты живешь,\n"
            "Введи команду в формате /weather city\n"
            "Я запомню тебя и в будущем уже не буду спрашивать ❤\n"
        )
    context.bot.send_message(chat_id=chat.id, text=message)

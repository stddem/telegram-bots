from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz
from aiogram import executor
import time


bot = Bot(token="6137719507:AAFX1w1OIlxgvvrAaDPASkpeLb_0xzgsbIg")

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

currency_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
currency_keyboard.add(KeyboardButton("USD"))
currency_keyboard.add(KeyboardButton("EUR"))
currency_keyboard.add(KeyboardButton("CNY"))
currency_keyboard.add(KeyboardButton("UAH"))
currency_keyboard.add(KeyboardButton("RUB"))

def get_actual_rate():
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    response = requests.get(url)

    root = ET.fromstring(response.content)

    for valute in root.findall(".//Valute"):
        if valute.find("CharCode").text == "KZT":
            rate = valute.find("Value").text.replace(",", ".")

    return float(rate)/100

activated_users = set()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    chat_id = message.chat.id
    if chat_id in activated_users:
        await bot.send_message(chat_id=chat_id, text="Вы уже активировали бота")
    else:
        activated_users.add(chat_id)
        await bot.send_message(chat_id=chat_id, text="Привет! Я умею отслеживать курсы валют к казахстанскому тенге. Выберите валюту, которую хотите отследить", reply_markup=currency_keyboard)

@dp.message_handler(lambda message: message.text in ["USD", "EUR", "CNY", "UAH", "RUB"])
async def handle_currency_selection(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in activated_users:
        await bot.send_message(chat_id=chat_id, text="Пожалуйста, активируйте бота с помощью команды /start")
        return

    currency = message.text
    rate = get_actual_rate()
    if rate is not None:
        await bot.send_message(chat_id=chat_id, text=f"Курс обмена {currency} на KZT составляет {rate}")
    else:
        await bot.send_message(chat_id=chat_id, text="Не удалось получить курс обмена.")

@dp.message_handler(commands=['stop'])
async def stop_command(message: types.Message):
    chat_id = message.chat.id
    if chat_id in activated_users:
        activated_users.remove(chat_id)
        await bot.send_message(chat_id=chat_id, text="Бот остановлен")
    else:
        await bot.send_message(chat_id=chat_id, text="Бот уже остановлен")

class DailyAPIRequester:
    def __init__(self, api_url, file_path):
        self.api_url = api_url
        self.file_path = file_path

    def make_request(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            with open(self.file_path, 'w') as file:
                file.write(response.text)
                print(f"XML raw код сохранен в файл: {self.file_path}")
        else:
            print("Код не сохранен")

    def run_daily(self):
        while True:
            now = datetime.now(pytz.timezone('Europe/Moscow'))
            target_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            time_diff = (target_time - now).total_seconds()
            time.sleep(time_diff)
            self.make_request()

if __name__ == "__main__":
    executor.start_polling(dp)
    api_url = "http://www.cbr.ru/scripts/XML_daily.asp"
    file_path = "daily_rates.xml"

    requester = DailyAPIRequester(api_url, file_path)
    requester.run_daily()




from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from datetime import date
import asyncio
import logging
import requests
from cachetools import TTLCache
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

API_TOKEN = "6249189353:AAGPSlM-l_CuUXzGeh6NS280pgROia5f1fE"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Несколько URL API для получения курса доллара, на случай, если какой-то будет недоступен
API_URL = {1:'https://api.exchangerate-api.com/v4/latest/usd',
           2:'https://www.cbr-xml-daily.ru/daily_json.js'}

# Комиссия (5%)
# Можно засунуть в класс
COMMISSION = 0.05

# Кэш с временем жизни 10 минут(16 часов), или запускать в отдельном потоке и зачищать, например в 10 часов каждый день
# Можно засунуть в класс
cache = TTLCache(maxsize=100, ttl=600)

# Состояния FSM
class Form(StatesGroup):
    waiting_for_exchange_rate = State()

# Функция для вычисления конечной суммы с комиссией
# Можно засунуть в класс
def calculate_total(amount, commission, exchange_rate):
    return exchange_rate * amount * (1 + commission)

# Функция обращающаяся к API для извлечения курса
# Можно засунуть в класс
def get_from_api(api_url, key):
    response = requests.get(api_url)
    if response.ok:
        data = response.json()
        if key == 2:
            exchange_rate = data['Valute']['USD']['Value']
        else:
            exchange_rate = data['rates']['RUB']
        cache[key] = exchange_rate
        return exchange_rate

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    kb = [
        [KeyboardButton(text="Нынешний курс")],
        [KeyboardButton(text="Посчитать курс с комиссией")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                   input_field_placeholder="Выберите нужное действие")
    await message.answer("Привет!\nЯ бот, который предоставляет актуальный курс доллара к рублю с учетом комиссии.",
                         reply_markup=keyboard)

# Обработчки кнопки "Нынешний курс"
@dp.message(F.text == "Нынешний курс")
async def get_exchange_rate(message: Message):
    for n in range(1, 3):
        exchange_rate = cache.get(n)
        if exchange_rate is not None:
            # Обращение в кэш
            await message.answer(f"На {date.today()} курс доллара составляет: {exchange_rate:.1f} руб.")
            break

        exchange_rate = get_from_api(API_URL[n], n)
        if exchange_rate is not None:
            await message.answer(f"На {date.today()} курс доллара составляет: {exchange_rate:.1f} руб.")
            break
        else:
            await message.answer("Ошибка, ни один источник данных не доступен")


# Обработчик кнопки "Посчитать курс"
@dp.message(F.text == "Посчитать курс с комиссией")
async def get_exchange_rate_command(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_for_exchange_rate)
    await message.reply("Введите сумму в долларах: ")

@dp.message(lambda message: message.text.isdigit())
async def process_amount(message: Message):
    for n in range(1, 3):
        exchange_rate = cache.get(n)
        if exchange_rate is not None:
            # Обращение в кэш
            print("Обращение")
            amount = float(message.text)
            total = calculate_total(amount, COMMISSION, exchange_rate)
            await message.answer(f"Курс доллара: {exchange_rate:.1f} руб. \nСумма с комиссией 5%: {total:.1f} руб.")
            break

        exchange_rate = get_from_api(API_URL[n], n)
        if exchange_rate is not None:
            amount = float(message.text)
            total = calculate_total(amount, COMMISSION, exchange_rate)
            await message.answer(f"Курс доллара: {exchange_rate:.1f} руб. \nСумма с комиссией 5%: {total:.1f} руб.")
            break
        else:
            await message.answer("Ошибка, ни один источник данных не доступен")

async def main() -> None:
    print("Start", datetime.now())
    await dp.start_polling(bot)
    print("Shutdown", datetime.now())

if __name__ == '__main__':
    # Логирование
    logging.basicConfig(level=logging.DEBUG, filename="bot_log.log", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())
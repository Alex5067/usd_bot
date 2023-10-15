# usd_bot

### Описание
Простой Telegram-бот, который предоставляет актуальный курс доллара к рублю и вычисляет его с учётом вложенной комиссии, и n-ым количеством долларов.

### Технологии
aiogram 3, Docker, logging, asyncio, TTLCache

### Алгоритм работы
Чтобы узнать нынешний курс доллара к рублю, нажимаем кнопку "Нынешний курс", чтобы перевести n-ое количество долларовк к рублю с учётом комиссии нажимаем "Посчитать курс с коммисией", вводим нужное кол-во долларов и получаем ответ.

### Команды
- /start - Приветствие, появляется при первом старте бота
Остальное взаимодействие реализовано с помощью кнопок.

## Запуск
1. Вписать свой токен бота в bot.py

        API_TOKEN = "YOUR_TOKEN"
   
2. Скачать/Склонировать репозиторий

        git clone https://github.com/Alex5067/usd_bot
        
3. `cd` в 'usd_bot' директорию

        docker-compose build
4. или

        python3 bot.py

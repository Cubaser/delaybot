# delaybot

## Описание
Это Telegram-бот для отложенных сообщений в группу Telegram.

### Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запуск бота |
| `/list` | Получение списка отложенных сообщений |
| `/add DD-MM-YYYY HH:MM` | Добавить отложенное сообщение |
| `/cancel_<ID>` | Отменить запланированное сообщение |
| `/chatid` | Получение ADMIN_ID и TARGET_GROUP_ID |

## Как начать работу с проектом?

### 1. Клонируйте репозиторий:
```bash
git clone git@github.com:Cubaser/delaybot.git
cd delaybot
```

### 2. Установка виртуального окружения и зависимостей
Активируйте виртуальное окружение и установите необходимые библиотеки:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
Создайте в корне проекта файл `.env` со следующим содержимым:
```env
TOKEN=<токен_вашего_бота>
ADMIN_ID=<ваш_telegram_id>
TARGET_GROUP_ID=<id_группы_куда_отправлять_сообщения>
```

### 4. Запустите бота:
```bash
python bot.py
```

### 5. Получения ADMIN_ID и TARGET_GROUP_ID:

Добавьте бота в нужную группу.
Назначьте бота администратором группы.
Отправьте в группе команду /chatid.
В ответ бот пришлёт идентификатор группы - это TARGET_GROUP_ID.

Напишите боту в личные сообщения команду /chatid
Бот отправит ваш личный идентификатор - это ADMIN_ID.

Добавьте полученные значения в переменные окружения (.env файл):
ADMIN_ID=123456789
TARGET_GROUP_ID=-1009876543210

После этого бот будет принимать команды только от указанного администратора, все отложенные сообщения будут автоматически отправляться в заданную группу.


### 6. Автозапуск через systemd:

Создаем файл.
```bash
sudo nano /etc/systemd/system/delaybot.service
```

Содержимое:
```nano
[Unit]
Description=Delay Bot
After=network.target

[Service]
User=root
WorkingDirectory=/home/USERNAME/delaybot
ExecStart=/home/USERNAME/delaybot/.venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Запускаем.
```bash
sudo systemctl daemon-reload
sudo systemctl enable delaybot.service
sudo systemctl start delaybot.service
```

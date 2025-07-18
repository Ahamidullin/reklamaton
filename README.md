# Фабрика персонажей - Telegram Bot

**Telegram-бот для создания и общения с AI-персонажами**

## 📋 Оглавление

1. [Описание проекта](#описание-проекта)
2. [Основные возможности](#основные-возможности)
3. [Архитектура](#архитектура)
4. [Установка и настройка](#установка-и-настройка)
5. [Структура проекта](#структура-проекта)
6. [API и интеграции](#api-и-интеграции)
7. [База данных](#база-данных)
8. [Разработка](#разработка)
9. [Команды бота](#команды-бота)
10. [Устранение неполадок](#устранение-неполадок)

## 📝 Описание проекта

**Фабрика персонажей** - это Telegram-бот, который позволяет пользователям создавать уникальных AI-персонажей и общаться с ними. Бот предоставляет два способа создания персонажей: через текстовый промпт или через детальный конструктор с настройкой характеристик.

### Главные особенности:
- **Создание персонажей**: Двухэтапный процесс создания (промпт/конструктор)
- **AI-диалоги**: Интеграция с Google Gemini API для генерации ответов
- **Генерация изображений**: Создание аватаров через DeepInfra API
- **Голосовые сообщения**: Поддержка voice-to-text через Google Speech-to-Text
- **Персистентность**: Сохранение истории диалогов и персонажей в базе данных

## 🚀 Основные возможности

### 1. Создание персонажей

#### Метод 1: Промпт-основанный
- Пользователь описывает персонажа в свободной форме
- Система создает персонажа на основе описания
- Возможность генерации аватара по текстовому описанию

#### Метод 2: Конструктор
- Выбор архетипа личности (MBTI): 16 типов в 4 группах
  - **Аналитики**: INTJ, INTP, ENTJ, ENTP
  - **Дипломаты**: INFJ, INFP, ENFJ, ENFP
  - **Стражи**: ISTJ, ISFJ, ESTJ, ESFJ
  - **Искатели**: ISTP, ISFP, ESTP, ESFP
- Выбор стиля общения:
  - Формальный, Литературный, Неформальный
  - Сленг (Gen Z), Сквернословие, Детский лепет
- Настройка черт характера (по шкале 1-5):
  - Сарказм, Юмор, Флирт, Непредсказуемость
  - Черный юмор (да/нет)

### 2. Система диалогов
- Полноценные AI-диалоги с контекстом
- Сохранение истории сообщений
- Поддержка текстовых и голосовых сообщений
- Активный персонаж (один на пользователя)

### 3. Управление персонажами
- Просмотр всех созданных персонажей
- Редактирование существующих персонажей
- Переключение между персонажами
- Предпросмотр перед сохранением

## 🏗️ Архитектура

### Основные компоненты:

```
reklamaton/
├── bot.py                    # Точка входа приложения
├── config.py                 # Конфигурация и переменные окружения
├── fsm/                      # Finite State Machine для создания персонажей
├── handlers/                 # Обработчики событий бота
├── keyboards/                # Inline-клавиатуры для интерфейса
├── models/                   # Модели данных (SQLAlchemy)
└── utils/                    # Вспомогательные функции (AI, обработка)
```

### Технологический стек:
- **Python 3.8+**
- **aiogram 3.5.0** - фреймворк для Telegram Bot API
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **aiosqlite** - асинхронный SQLite драйвер
- **Google Gemini API** - генерация AI-ответов
- **DeepInfra API** - генерация изображений
- **Google Speech-to-Text** - распознавание речи

## ⚙️ Установка и настройка

### 1. Системные требования
```bash
Python 3.8+
SQLite (включен в Python)
```

### 2. Установка зависимостей
```bash
# Клонирование репозитория
git clone <repository-url>
cd reklamaton

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
Создайте файл `.env` в корневой папке проекта:

```env
# Telegram Bot API
BOT_TOKEN=your_telegram_bot_token_here

# Google APIs (опционально - для использования Gemini)
GOOGLE_API_KEY=your_google_api_key_here

# DeepInfra API (для генерации изображений и/или текста)
DEEPINFRA_API_KEY=your_deepinfra_api_key_here

# База данных (опционально)
DB_URL=sqlite+aiosqlite:///reklamaton.db
```

### 4. Получение API ключей

#### Telegram Bot Token:
1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Создайте нового бота командой `/newbot`
3. Скопируйте полученный токен

#### Google API Key:
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект или выберите существующий
3. Включите APIs:
   - Generative AI API (для Gemini)
   - Speech-to-Text API
4. Создайте API ключ в разделе "Credentials"

#### DeepInfra API Key:
1. Зарегистрируйтесь на [DeepInfra](https://deepinfra.com/)
2. Получите API ключ в профиле

### ⚠️ Важно: Приоритет API ключей
- Если задан `GOOGLE_API_KEY` → используется Google Gemini для генерации текста
- Если `GOOGLE_API_KEY` не задан, но есть `DEEPINFRA_API_KEY` → используется DeepInfra Mistral для генерации текста
- Для генерации изображений всегда используется DeepInfra (требует `DEEPINFRA_API_KEY`)
- Необходим хотя бы один из ключей для корректной работы бота

### 5. Запуск бота
```bash
python bot.py
```

## 📁 Структура проекта

### Детальное описание модулей:

#### `/handlers/` - Обработчики событий
- **`general.py`** - Основные команды (/start, главное меню)
- **`character_creation.py`** - Создание и редактирование персонажей
- **`character_selection.py`** - Выбор и активация персонажей
- **`dialogue.py`** - Обработка диалогов (текст и голос)

#### `/models/` - Модели данных
- **`base.py`** - Базовая конфигурация SQLAlchemy
- **`engine.py`** - Движок базы данных и создание таблиц
- **`user.py`** - Модель пользователя
- **`character.py`** - Модель персонажа
- **`message.py`** - Модель сообщения
- **`active_character.py`** - Связь пользователя с активным персонажем

#### `/keyboards/` - Интерфейс
- **`inline.py`** - Все inline-клавиатуры для навигации

#### `/fsm/` - Состояния создания персонажей
- **`character_creation.py`** - FSM для процесса создания

#### `/utils/` - Утилиты
- **`ai.py`** - Интеграция с AI APIs (Gemini, DeepInfra, Speech-to-Text)

## 🔌 API и интеграции

### LLM Integration (Google Gemini / DeepInfra)
```python
# Основная функция: get_gemini_response()
# Автоматическое переключение между провайдерами:
# - Если есть GOOGLE_API_KEY -> используется Google Gemini (gemini-2.5-flash)
# - Если нет GOOGLE_API_KEY, но есть DEEPINFRA_API_KEY -> используется DeepInfra Mistral
# - Если нет ни одного ключа -> показывается сообщение об ошибке
```

### Google Gemini API
```python
# Модель: gemini-2.5-flash
# Функции: get_gemini_response() (при наличии GOOGLE_API_KEY)
# Особенности: Динамическое создание system prompt на основе характеристик персонажа
```

### DeepInfra API
```python
# Текст: mistralai/Mistral-Small-3.2-24B-Instruct-2506
# Изображения: black-forest-labs/FLUX-1-schnell
# Функции: get_deepinfra_response(), generate_image_with_deepinfra()
# Параметры изображений: 1024x1024, 25 inference steps
# Параметры текста: temperature=0.7, max_tokens=1000
```

### Google Speech-to-Text
```python
# Конфигурация: OGG_OPUS, 48kHz, ru-RU
# Функции: get_text_from_speech()
```

### Telegraph API
```python
# Загрузка изображений для отображения в Telegram
# Функции: upload_to_telegraph()
```

## 🗄️ База данных

### Схема базы данных:

#### Таблица `users`
```sql
id INTEGER PRIMARY KEY
telegram_id BIGINT UNIQUE NOT NULL
```

#### Таблица `characters`
```sql
id INTEGER PRIMARY KEY
name VARCHAR(100) NOT NULL
description TEXT
avatar_file_id VARCHAR
is_premade BOOLEAN DEFAULT FALSE
user_id INTEGER FOREIGN KEY
-- Характеристики конструктора:
archetype VARCHAR
communication_style VARCHAR
sarcasm_level INTEGER
humor_level INTEGER
flirt_level INTEGER
unpredictability_level INTEGER
has_black_humor BOOLEAN
```

#### Таблица `messages`
```sql
id INTEGER PRIMARY KEY
user_id INTEGER FOREIGN KEY
character_id INTEGER FOREIGN KEY
role VARCHAR(10) -- 'user' или 'model'
content TEXT
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
```

#### Таблица `active_characters`
```sql
user_id INTEGER FOREIGN KEY
character_id INTEGER FOREIGN KEY
PRIMARY KEY (user_id)
```

## 🛠️ Разработка

### Добавление новых функций

#### Создание нового обработчика:
```python
from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(F.text.startswith("/new_command"))
async def new_command_handler(message: Message):
    await message.answer("Новая команда")
```

#### Добавление в главный файл:
```python
# В bot.py
from handlers import new_handler
dp.include_router(new_handler.router)
```

### Работа с базой данных:
```python
from models.base import async_session
from sqlalchemy import select

async def get_user_characters(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Character).where(Character.user_id == user_id)
        )
        return result.scalars().all()
```

### Добавление новых AI интеграций:
```python
# В utils/ai.py
async def new_ai_function(prompt: str) -> str:
    # Ваша логика интеграции
    pass
```

## 🤖 Команды бота

### Пользовательские команды:
- `/start` - Запуск/перезапуск бота
- `/my_characters` - Просмотр всех персонажей

### Callback-команды (inline кнопки):
- `main_menu` - Главное меню
- `select_character` - Выбор персонажа
- `create_character` - Создание персонажа
- `start_dialogue_{id}` - Начать диалог с персонажем
- `edit_character_{id}` - Редактировать персонажа

## 🔧 Устранение неполадок

### Частые проблемы:

#### 1. Ошибка подключения к API
```
Error calling Gemini API: ...
```
**Решение**: Проверьте `GOOGLE_API_KEY` в `.env` файле

#### 2. Ошибка генерации изображений
```
Error calling Deep Infra API: ...
```
**Решение**: Проверьте `DEEPINFRA_API_KEY` и лимиты аккаунта

#### 3. Проблемы с базой данных
```
sqlite3.OperationalError: no such table: ...
```
**Решение**: Удалите `reklamaton.db` и перезапустите бота

#### 4. Ошибка распознавания речи
```
Error calling Speech-to-Text API: ...
```
**Решение**: Проверьте настройки Google Cloud API

### Логирование
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Режим отладки
```python
# В bot.py измените на:
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Планы развития

### Возможные улучшения:
1. **Групповые чаты**: Поддержка нескольких персонажей в одном чате
2. **Экспорт/импорт**: Возможность делиться персонажами
3. **Премиум функции**: Расширенные возможности создания
4. **Аналитика**: Статистика использования персонажей
5. **Мультиязычность**: Поддержка других языков
6. **Веб-интерфейс**: Управление персонажами через веб
7. **API персонажей**: Внешний API для интеграции
8. **Эмоции**: Система эмоциональных состояний персонажей

## 👥 Контакты и поддержка

При возникновении вопросов или проблем:
1. Проверьте этот README
2. Изучите код в соответствующих модулях
3. Проверьте логи приложения
4. Обратитесь к документации используемых API

---

**Удачи в разработке! 🚀**

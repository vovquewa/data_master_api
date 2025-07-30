# Data Master API

**Excel data processing service**

## 📘 Документация

Интерактивная документация доступна по адресу:

```
http://localhost:8000/docs
```

Все эндпоинты ктоме тестовых требуют авторизации через Bearer Token.  
Пример заголовка авторизации:

```
Authorization: Bearer <your_token_here>
```

---

## 🚀 Установка и запуск

1. Создайте директорию проекта:

   ```bash
   mkdir app
   cd app
   ```

2. Создайте необходимые папки:

   ```bash
   mkdir env
   mkdir logs
   ```

3. Сконфигурируйте переменные окружения:

   - Создайте файл `.env` в папке `env` по аналогии с `env.example`, добавив токен.

4. Скопируйте файл `docker-compose.yml` из репозитория в корень папки `app`.

5. Запустите сервис:
   ```bash
   docker-compose up -d
   ```

---

## 🔐 Авторизация

- Используется **Bearer Token**.

---

## 📂 Структура проекта

```
app/
├── env/             # Переменные окружения
│   └── .env
├── logs/            # Логи приложения
├── docker-compose.yml
└── ...
```

---

## 🛠 Стек технологий

- Python 3.13
- FastAPI
- Docker / Docker Compose
- Uvicorn
- Pydantic
- Pandas

---

## 📝 Лицензия

Файл LICENSE

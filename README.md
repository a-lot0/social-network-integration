Социальная сеть (микроблог)

Микросервисная социальная сеть с возможностью создания постов, подписок и ленты новостей.

# Архитектура

| Сервис | Порт | Описание |
|--------|------|----------|
| Profile Service | 5001 | Управление профилями |
| Post Service | 5002 | Управление постами |
| Feed Service | 5003 | Управление подписками и лентой |
| PostgreSQL | 5432 | База данных |

Запуск проекта

# Требования
- Python 3.11+
- Docker (опционально)
- PostgreSQL (или Docker)

# Локальный запуск

git bash

# Клонирование репозитория
git clone https://github.com/a-lot0/social-network-integration.git
cd social-network-integration

# Установка зависимостей
pip install -r profile-service/requirements.txt
pip install -r post-service/requirements.txt
pip install -r feed-service/requirements.txt

# Запуск сервисов (в разных терминалах)
cd profile-service && python app.py
cd ../post-service && python app.py
cd ../feed-service && python app.py

# Запуск через Docker Compose
docker-compose up --build

# Запуск фронтенда
cd ../social-network-frontend
python -m http.server 8080

# Примеры запросов
# Создание пользователя
curl -X POST http://localhost:5001/profile \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@test.com","bio":"Hello"}'

# Создание поста
curl -X POST http://localhost:5002/posts \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"content":"My first post!"}'

# Подписка
curl -X POST http://localhost:5003/subscribe \
  -H "Content-Type: application/json" \
  -d '{"follower_id":1,"following_id":2}'

# Получение ленты
curl http://localhost:5003/feed/1

# Установка pytest
pip install pytest

# Запуск всех тестов
pytest tests/ -v

# Запуск только unit-тестов
pytest tests/unit/ -v

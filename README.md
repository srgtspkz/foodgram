# Фудграм

Фудграм — веб-приложение для создания и хранения рецептов.

Пользователи могут создавать и редактировать рецепты, загружать изображения, подписываться на авторов, добавлять рецепты в избранное и корзину покупок, а также формировать общий список ингредиентов для покупки.

## Сайт

[Открыть Фудграм](https://srgtspkz-foodgram.myddns.me)

## Возможности

- регистрация и авторизация пользователей;
- создание, редактирование и удаление рецептов;
- загрузка изображений рецептов и аватаров;
- подписки на авторов;
- добавление рецептов в избранное;
- добавление рецептов в корзину покупок;
- формирование и скачивание списка покупок;
- фильтрация рецептов по тегам;
- поиск ингредиентов по названию;
- короткие ссылки на рецепты;
- административная панель;
- импорт и экспорт ингредиентов;
- пагинация результатов.

## Технологии

| Технология            | Назначение                              |
| --------------------- | --------------------------------------- |
| Python 3.12.3         | Основной язык backend                   |
| Django                | Backend-фреймворк                       |
| Django REST Framework | API                                     |
| Djoser                | Авторизация и управление пользователями |
| django-filter         | Фильтрация данных                       |
| django-import-export  | Импорт и экспорт ингредиентов           |
| PostgreSQL 16.15      | База данных                             |
| Gunicorn              | WSGI-сервер                             |
| Docker                | Контейнеризация                         |
| Docker Compose        | Запуск сервисов                         |
| Nginx                 | Веб-сервер                              |
| React                 | Frontend                                |
| GitHub Actions        | CI/CD                                   |

## Структура проекта

```text
foodgram/
├── .github/
│   └── workflows/
├── backend/
│   ├── api/
│   ├── backend/
│   ├── recipes/
│   ├── users/
│   ├── utils/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── manage.py
│   └── requirements.txt
├── data/
│   ├── ingredients.csv
│   └── ingredients.json
├── docs/
│   ├── openapi-schema.yml
│   └── redoc.html
├── frontend/
│   ├── public/
│   ├── src/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── package-lock.json
│   └── package.json
├── infra/
│   ├── docker-compose.yml
│   └── nginx.conf
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
├── postman_collection/
│   └── foodgram.postman_collection.json
├── venv/
├── .env
├── .gitignore
├── docker-compose.production.yml
├── docker-compose.yml
├── README.md
└── setup.cfg
```

## Переменные окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=твой-секретный-ключ
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,ваш-домен
CSRF_TRUSTED_ORIGINS=https://ваш-домен

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=ваш-пароль
POSTGRES_HOST=db # локально: localhost
POSTGRES_PORT=5432

DATA_UPLOAD_MAX_NUMBER_FIELDS=10000
```

Для запуска через Docker в `POSTGRES_HOST` используется имя сервиса PostgreSQL — `db`. При локальном запуске backend укажите `localhost`.

## Запуск проекта через Docker

Из корневой директории проекта выполните:

```bash
docker compose up -d --build
```

Проверить состояние контейнеров:

```bash
docker compose ps
```

Применить миграции:

```bash
docker compose exec backend python manage.py migrate
```

Собрать статические файлы Django:

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

Создать суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

После запуска приложение будет доступно по адресу:

```text
http://localhost/
```

Административная панель:

```text
http://localhost/admin/
```

API:

```text
http://localhost/api/
```

## CI/CD

Для проекта настроен CI/CD с использованием GitHub Actions.

Автоматизация включает:

- проверку кода;
- запуск тестов;
- сборку Docker-образов;
- публикацию Docker-образов;
- развёртывание проекта на сервере;
- применение миграций;
- сбор статических файлов;
- перезапуск контейнеров.

## Локальный запуск backend

Создайте виртуальное окружение:

```bash
python -m venv venv
```

Для Windows:

```bash
source venv/Scripts/activate
```

Обновите:

```bash
python -m pip install --upgrade pip
```

Перейдите в директорию backend:

```bash
cd backend
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Для локального запуска измените в `.env`:

```env
POSTGRES_HOST=localhost
```

Примените миграции:

```bash
python manage.py migrate
```

Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

Запустите сервер:

```bash
python manage.py runserver
```

## Основные API-маршруты

### Пользователи

```text
POST   /api/users/
GET    /api/users/
GET    /api/users/{id}/
GET    /api/users/me/
GET    /api/users/subscriptions/
POST   /api/users/{id}/subscribe/
DELETE /api/users/{id}/subscribe/
PUT    /api/users/me/avatar/
DELETE /api/users/me/avatar/
```

### Авторизация

```text
POST /api/auth/token/login/
POST /api/auth/token/logout/
```

### Теги

```text
GET /api/tags/
GET /api/tags/{id}/
```

### Ингредиенты

```text
GET /api/ingredients/
GET /api/ingredients/{id}/
GET /api/ingredients/?name=мол
```

### Рецепты

```text
GET    /api/recipes/
POST   /api/recipes/
GET    /api/recipes/{id}/
PATCH  /api/recipes/{id}/
DELETE /api/recipes/{id}/
GET    /api/recipes/{id}/get-link/
```

### Избранное

```text
POST   /api/recipes/{id}/favorite/
DELETE /api/recipes/{id}/favorite/
```

### Корзина покупок

```text
POST   /api/recipes/{id}/shopping_cart/
DELETE /api/recipes/{id}/shopping_cart/
GET    /api/recipes/download_shopping_cart/
```

## Авторизация

Для получения токена используется email и пароль:

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

Токен передаётся в заголовке:

```text
Authorization: Token <token>
```

## Автор

[Сергей Цепилов](https://github.com/srgtspkz)

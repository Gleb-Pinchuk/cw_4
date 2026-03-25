# Курсовая работа: Habit Tracker API

Backend часть SPA веб-приложения для отслеживания полезных привычек на основе книги Джеймса Клира «Атомные привычки». Реализовано на Python с использованием Django и Django Rest Framework.

## Возможности

CRUD операции для управления привычками (создание, чтение, обновление, удаление)
JWT авторизация: регистрация и вход пользователей с выдачей токенов
Валидация данных:
Приятная привычка не может иметь вознаграждения или связанной привычки
Полезная привычка не может иметь одновременно и вознаграждение, и связанную привычку
Связанная привычка должна иметь признак «приятной»
Время выполнения привычки — не более 2 минут
Периодичность выполнения — от 1 до 7 дней
Пагинация: вывод списка привычек по 5 элементов на страницу
Права доступа:
Пользователь имеет полный доступ только к своим привычкам
Публичные привычки доступны всем на чтение
Интеграция с Telegram: отправка напоминаний о привычках через бота
Отложенные задачи: периодическая проверка и рассылка уведомлений через Celery + Redis
Переменные окружения: безопасное хранение секретных данных в .env
CORS: настройка для подключения фронтенда
Документация API: интерактивная Swagger-документация через drf-spectacular
Тестирование: покрытие тестами > 80% с использованием pytest/django test
Качество кода: проверка через Flake8 (100% без учёта миграций)

### Локальный запуск

```bash
# 1. Клонируй репозиторий
git clone https://github.com/Gleb-Pinchuk/cw_4.git
cd cw_4

# 2. Создай .env файл
cp .env.example .env
# Отредактируй .env (SECRET_KEY, TELEGRAM_BOT_TOKEN)

# 3. Запусти Docker
docker compose up -d

# 4. Примени миграции
docker compose exec web python manage.py migrate

# 5. Создай суперпользователя
docker compose exec web python manage.py createsuperuser

#Развёртывание на удалённом сервере

## Обновление пакетов
sudo apt update && sudo apt upgrade -y

## Установка Docker
curl -fsSL https://get.docker.com | sh

## Добавление пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER
newgrp docker

## Проверка установки
docker --version
docker compose version

##Клонирование проекта

git clone https://github.com/Gleb-Pinchuk/cw_4.git
cd cw_4

## Создай .env файл из шаблона
cp .env.example .env

#Сборка и запуск

# Собери Docker-образ (установит все зависимости)
docker build -t cw_4-web:latest .

# Запусти все сервисы
docker compose up -d

 #Первоначальная настройка

# Примени миграции 
docker compose exec web python manage.py migrate

# Собери статику для Nginx
docker compose exec web python manage.py collectstatic --noinput

# Создай суперпользователя для входа в админку
docker compose exec web python manage.py createsuperuser



Доступ: Админка http://<IP_СЕРВЕРА>:8081/admin/
Документация API http://<IP_СЕРВЕРА>:8081/api/docs/

WEB-сайт http://83.166.236.188:8081/admin/login/?next=/admin/

## Лицензия
Этот проект создан в учебных целях в рамках курсовой работы. Использование кода разрешено с указанием авторства.

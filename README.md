# 🍽 Foodgram

## Описание проекта:
**Foodgram** — сайт, на котором пользователи публикуют свои рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Зарегистрированным пользователям доступен сервис **«Список покупок»**, который позволяет формировать список ингредиентов для выбранных блюд.

---

## 🔗 Развернутый проект:
[https://foodgramstudy.zapto.org](https://foodgramstudy.zapto.org).  
   
![CI Status](https://github.com/Iceberen/foodgram/actions/workflows/main.yml/badge.svg)

---

## 🛠 Технологии

- **Python 3.9**
- **Django 3.2**
- **Django REST Framework**
- **PostgreSQL**
- **Gunicorn**
- **Nginx**
- **Docker & Docker Compose**
- **React** (Frontend)
- **GitHub Actions** (CI/CD)

---

## 🚀 Локальный запуск проекта
1. Клонировать репозиторий
  ```
  git clone https://github.com/Iceberen/foodgram.git
  cd foodgram
  ```
2. Создать и заполнить файл `.env`. Все необходимые переменные в файле `.env.example`
  ```
  cp .env.example .env
  # Откройте .env и укажите свои настройки
  ```
3. Запустить Docker-контейнеры
  ```
  docker compose -f docker-compose.yml up -d --build
  ```
4. Применить миграции и собрать статику
  ```
  docker compose exec backend python manage.py migrate
  docker compose exec backend python manage.py collectstatic --noinput
  docker compose exec backend python manage.py loaddata data/ingredients.json
  ```
5. Создать суперпользователя
  ```
  docker compose exec backend python manage.py createsuperuser
  ```
6. Готово! После запуска проект будет доступен:
  ```
  http://localhost/
  http://localhost/admin/ # Админка
  ```

---

## 🌍 Деплой на сервер
1. Подключиться к серверу
  ```
  ssh user@your_server_ip
  ```
2. Установить Docker и Docker Compose (если не установлены)
3. Клонировать проект на сервер
  ```
  git clone https://github.com/Iceberen/foodgram.git
  cd foodgram
  ```
4. Создать `.env` с нужными настройками для продакшена
5. Запустить проект
  ```
  docker compose -f infra/docker-compose.yml up -d --build
  ```

---

## ⚙️ CI/CD
В проекте настроен **GitHub Actions** для автоматического деплоя:
- При пуше в ветку `main`:
  - Код проходит тесты (`flake8`, `pytest`)
  - Проект собирается в Docker-образ и отправляется на Docker Hub
  - Выполняется деплой на сервер через SSH

---

## 📂 Структура проекта
```
foodgram/
├── backend/ # Исходный код Django-приложения (API)
├── frontend/ # Исходный код фронтенда (React)
├── infra/ # Docker-конфигурации и настройки для деплоя
├── docs/ # Документация API
├── data/ # Статические данные (ингредиенты и т.д.)
└── README.md # Описание проекта
```

---

## 🧑‍💻 Автор
Разработано: [Iceberen](https://github.com/Iceberen) в рамках дипломной работы по курсу "Python-разработчик" от ЯП.

---
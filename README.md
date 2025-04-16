# Проект «Foodgram»

## Описание проекта:
«Foodgram»  сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
#### Развернутый проект:
[https://foodgramstudy.zapto.org](https://foodgramstudy.zapto.org)
#### Cостояние рабочего процесса в GitHub:
![CI Status](https://github.com/Iceberen/foodgram/actions/workflows/main.yml/badge.svg)

# Как запустить проект:
*Примечание: Все примеры указаны для Linux*
## Локально
*Примечание: Для локального запуска проекта используется `docker-compose.yml`*
### Установка
- Клонировать репозиторий и перейти в него в командной строке:
  ```
  git clone https://github.com/Iceberen/foodgram.git
  cd foodgram
  ```
- Создать файл `.env` и заполните его своими данными. Все необходимые переменные перечислены в файле `.env.example.`
### Запуск `Docker compose`
1. Из корневой папки проекта выполните команду:
  ```
  docker compose up --build
  ```
2. Из корневой папки проекта выполните миграции:
  ```
  docker compose exec backend python manage.py migrate 
  ```
3. Из корневой папки проекта выполните команды сборки и копирования статики:
  ```
  docker compose exec backend python manage.py collectstatic
  docker compose exec backend cp -r /app/collected_static/. /static/static/
  ```
4. Из корневой папки проекта выполните команду записи в БД ингидиентов :
  ```
  docker compose exec backend python manage.py load_db
  ```
5. Проект развернут и готов к работе на [https://localhost:8080](https://localhost:8080)
## На удаленном сервере
*Примечание: Для запуска проекта на удаленном сервере используется `docker-compose.production.yml`*
### Установка
- Клонировать репозиторий и перейти в него в командной строке:
  ```
  git clone https://github.com/Iceberen/foodgram.git
  cd foodgram
  ```
- Создать файл `.env` и заполните его своими данными. Все необходимые переменные перечислены в файле `.env.example.`

### Создание Docker-образов
1. Из корневой папки проекта выполните команды из листинга при этом замените `username` на свой логин на `DockerHub`:
  ```
  cd frontend
  docker build -t username/foodgram_frontend .
  cd ../backend
  docker build -t username/foodgram_backend .
  cd ../nginx
  docker build -t username/foodgram_gateway . 
  ```
2. Загрузите образы на `DockerHub`, заменив `username` на свой логин на `DockerHub`:
  ```
  docker push username/foodgram_frontend
  docker push username/foodgram_backend
  docker push username/foodgram_gateway
  ```

### Деплой на сервере
1. Подключитесь к удаленному серверу:
  ```
  ssh -i "путь_до_ключа_SSH"/"имя_файла_ключа_SSH" username@IP_adress_server
  ```
2. Создайте на сервере директорию `foodgram`:
  ```
  mkdir foodgram
  ```
3. Установите `Docker Compose` на сервер:
  ```
  sudo apt update
  sudo apt install curl
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo apt install docker-compose
  ```
4. Скопируйте файлы `docker-compose.production.yml` и `.env` в директорию `foodgram/` на сервере:
  ```
  scp -i "путь_до_ключа_SSH"/"имя_файла_ключа_SSH" docker-compose.production.yml /  
  username@IP_adress_server:/home/username/foodgram/docker-compose.production.yml
  ```
  и
  ```
  scp -i "путь_до_ключа_SSH"/"имя_файла_ключа_SSH" .env /  
  username@IP_adress_server:/home/username/foodgram/.env
  ```
5. Запустите `Docker Compose` в режиме демона:
  ```
  sudo docker-compose -f /home/username/foodgram/docker-compose.production.yml up -d
  ```
6. Выполните миграции, соберите статические файлы бэкенда, скопируйте их в `/static/static/` и заполните БД ингредиентами:
  ```
  sudo docker-compose -f /home/username/kittygram/docker-compose.production.yml exec backend python manage.py migrate
  sudo docker-compose -f /home/username/kittygram/docker-compose.production.yml exec backend python manage.py collectstatic
  sudo docker-compose -f /home/username/kittygram/docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
  sudo docker-compose -f /home/username/kittygram/docker-compose.production.yml exec backend python manage.py load_db
  ```
7. Откройте конфигурационный файл `Nginx` в редакторе `nano`:
  ```
  sudo nano /etc/nginx/sites-enabled/default
  ```
8. Измените настройки `location` в секции `server`:
  ```
  location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8080;
  }
  ```
9. Проверьте правильность конфигурации `Nginx`:
  ```
  sudo nginx -t
  ```
10. Перезапустите `Nginx`:
  ```
  sudo service nginx reload
  ```

## Настройка CI/CD
1. Файл `workflow` уже написан и находится в директории:
  ```
  /.github/workflows/main.yml
  ```
2. Добавьте секреты в GitHub Actions:
  ```
  DOCKER_USERNAME                # имя пользователя в DockerHub
  DOCKER_PASSWORD                # пароль пользователя в DockerHub
  HOST                           # IP-адрес сервера
  USER                           # имя пользователя
  SSH_KEY                        # содержимое приватного SSH-ключа
  SSH_PASSPHRASE                 # пароль для SSH-ключа
  TELEGRAM_TO                    # ID вашего телеграм-аккаунта
  TELEGRAM_TOKEN                 # токен вашего бота
  ```

## Технологии
- Python
- Django
- DjangoRestFramework
- PostgreSQL

## Автор
[Васильев Вячеслав](https://github.com/Iceberen)
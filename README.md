# Проект «Продуктовый помощник»
#### Описание:
Проект «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Проект доступен по адресу http://51.250.73.251/

####  Как развернуть проект на Яндекс облаке:
```
cd /d/Dev
```
Клонируем репозиторий:
```
git@github.com:asp781/foodgram-project-react.git
```
Создаем файл .env и копируем его в директорию infra:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
Переходим
```
cd /d/Dev/foodgram-project-react
```
Копируем директорию infra и docs на сервер
```
scp -r infra/ asp78@51.250.73.251:
scp -r docs/ asp78@51.250.73.251:
```
Заходим на сервер
```
ssh asp78@51.250.73.251
```
Устанавливаем на сервере:
```
sudo apt install docker.io
```
```
sudo apt install docker-compose
```
На сервере переходим в папку infra
```
cd infra
```
Загружаем образы с DockerHub:
```
sudo docker-compose pull
```
Создаем контейнеры:
```
sudo docker-compose up -d
```
Выполняем миграции:
```
sudo docker-compose exec backend python manage.py migrate
```
Заполняем базу тестовыми данными:
```
sudo docker-compose exec backend python manage.py loaddata fixtures.json
```
Собираем статику:
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
Теперь проект доступен по адресу

http://51.250.73.251/

Вход в админку

http://51.250.73.251/admin/

## Технологии:
- Python 3.8
- Django 2.2.19
- djangorestframework 3.12.4
- Docker
- NGINX
- GUNICORN
- POSTGRES

Автор проекта: [Алексей Спесивцев](https://github.com/asp781/)

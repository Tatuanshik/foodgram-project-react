[![CI и CD проекта foodgram-project-react](https://github.com/Tatuanshik/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Tatuanshik/foodgram-project-react/actions/workflows/main.yml//)

Страница сайта доступна по адресу: http://84.201.166.178/

# Описание

### Сайт - Foodgram, «Продуктовый помощник». На сайте вы можете создавать свои рецепты, просматривать рецепты других пользователей, подписываться на интересных вам авторов, добавлять лучшие рецепты в избранное, а также создавать и скачивать список покупок

# Запускаем проект:

***Клонировать репозитарий:git@github.com:Tatuanshik/foodgram-project-react.git***
- cd backend

***Создать виртуальное окружение***
- ```python -m venv env или python3 -m venv env (Mac)```
- ``` source env/Scripts/activate или source venv/bin/activate (Mac) ```

## Установить зависимости из файла requirements.txt:
- ***```python3 -m pip install --upgrade pip```***
- ***```pip install -r backend/foodgram/requirements.txt```***

## Из директории infra/:Запустить проект в контейнере
- ***```docker-compose up -d --build```***

## Выполняем миграции:
- ***``` sudo docker-compose exec web python manage.py migrate```***
## Загрузить ингредиенты: 
- ***``` sudo docker-compose exec web python manage.py load_ingredients```***
## Создаем суперпользователя:
- ***``` sudo docker-compose exec web python manage.py createsuperuser```***

### Остановка контейнера:
- ***```sudo docker-compose down -v```***

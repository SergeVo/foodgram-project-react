# FOODRGAM
## Дипломный проект: Продуктовый помощник
![example workflow](https://github.com/SergeVo/foodgram-project-react/actions/workflows/main.yml/badge.svg)


# Возможности платформы

## Публикация Рецептов
Пользователи могут создавать и публиковать собственные рецепты блюд. Это предоставляет возможность делиться своими кулинарными идеями с сообществом.

## Избранное
Пользователи имеют возможность добавлять чужие рецепты в свой список избранных. Это позволяет быстро находить и сохранять интересные рецепты для будущего использования.

## Подписки
Пользователи могут подписываться на активность других авторов рецептов. Эта функция позволяет пользователям получать уведомления о новых публикациях и обновлениях от выбранных авторов.

## Список покупок
Для удобства планирования и подготовки к приготовлению блюд, пользователи могут создавать список продуктов, необходимых для выбранных рецептов. Это помогает им эффективно организовывать покупки и не забывать необходимые ингредиенты.



## **Описание проекта**

Проект находится по адресу: https://servofoodgram.ru/

## **Технологии:**

* [Python 3.9](https://www.python.org/downloads/)
* [Django 3.2.3](https://www.djangoproject.com/download/)
* [djangorestframework 3.12.4](https://pypi.org/project/djangorestframework/#files)
* [djoser 2.1.0](https://pypi.org/project/djoser/#files)
* [gunicorn 20.1.0](https://pypi.org/project/gunicorn/20.1.0/)
* [psycopg2-binary 2.9.6](https://pypi.org/project/psycopg2-binary/#files)
* [pytest-django 4.4.0](https://pypi.org/project/pytest-django/)
* [pytest-pythonpath 0.7.3](https://pypi.org/project/pytest-pythonpath/)
* [pytest 6.2.4](https://pypi.org/project/pytest/)
* [python-dotenv 1.0.0](https://pypi.org/project/python-dotenv/)

## Локальный запуск проекта

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/SergeVo/foodgram-project-react
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение, установить зависимости:

```bash
python3 -m venv venv && \ 
    source venv/scripts/activate && \
    python -m pip install --upgrade pip && \
    pip install -r backend/requirements.txt
```

Установите [docker compose](https://www.docker.com/) на свой компьютер.

Запустите проект через docker-compose:

```bash
docker compose -f docker-compose.yml up --build -d
```

Выполнить миграции:

```bash
docker compose -f docker-compose.yml exec backend python manage.py migrate
```

Соберите статику и скопируйте ее:

```bash
docker compose -f docker-compose.yml exec backend python manage.py collectstatic  && \
docker compose -f docker-compose.yml exec backend cp -r /app/static_backend/. /backend_static/
```

## .env

В корне проекта создайте файл .env и пропишите в него свои данные.

Пример:

```apache
SECRET_KEY = 'my_secret_key'
POSTGRES_DB=db
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=dbpass
DB_NAME=food
DB_HOST=db
DB_PORT=5432 
DEBUG=False
ALLOWED_HOSTS = '***.**', '**.***.**.***', '127.0.0.1', 'localhost'
USE_SQLITE=False
```

## Workflow

Для использования Continuous Integration (CI) и Continuous Deployment (CD): в репозитории GitHub Actions `Settings/Secrets/Actions` прописать Secrets - переменные окружения для доступа к сервисам. Они автоматически добавятся в файл .env при развертывании контейнера:

```
DOCKER_USERNAME                # имя пользователя в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub
HOST                           # ip_address сервера
USER                           # имя пользователя
SSH_KEY                        # приватный ssh-ключ (cat ~/.ssh/id_rsa)
PASSPHRASE                     # кодовая фраза (пароль) для ssh-ключа
DB_NAME                        # имя БД
DB_PORT                        # порт БД
DEBUG                          # True или False
ALLOWED_HOSTS                  # ваши хосты
TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
```

При push в ветку main автоматически отрабатывают сценарии:

* *tests* - проверка кода на соответствие стандарту PEP8 и запуск pytest. Дальнейшие шаги выполняются только если push был в ветку main;
* *build\_and\_push\_to\_docker\_hub* - сборка и доставка докер-образов на DockerHub
* *deploy* - автоматический деплой проекта на боевой сервер. Выполняется копирование файлов из DockerHub на сервер;
* *send\_message* - отправка уведомления в Telegram.

## Автор Догадин Сергей.


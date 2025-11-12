FROM python:3.13

WORKDIR /main

# Копирование зависимостей
COPY requirements.txt /main/

# Установка зависимостей Python и утилиты yc
RUN apt-get update && apt-get install -y openssh-client curl \
    && pip install --no-cache-dir -r requirements.txt \
    && ln -snf /usr/share/zoneinfo/Asia/Yekaterinburg /etc/localtime && echo "Asia/Yekaterinburg" > /etc/timezone


COPY app /main/app
# Добавление переменных окружения
ENV PYTHONPATH "${PYTHONPATH}:/main"
CMD ["python3", "-u", "./app/main.py"]
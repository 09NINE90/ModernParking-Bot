FROM python:3.13

WORKDIR /main

ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG BOT_TOKEN
ARG GROUP_ID
ARG DELAY_MINUTES_CONFIRM_SPOT
ARG LOGS_CHANNEL_ID
ARG FEEDBACK_CHANNEL_ID

ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV DB_NAME=$DB_NAME
ENV BOT_TOKEN=$BOT_TOKEN
ENV GROUP_ID=$GROUP_ID
ENV DELAY_MINUTES_CONFIRM_SPOT=$DELAY_MINUTES_CONFIRM_SPOT
ENV LOGS_CHANNEL_ID=$LOGS_CHANNEL_ID
ENV FEEDBACK_CHANNEL_ID=$FEEDBACK_CHANNEL_ID
ENV PYTHONPATH="/app"


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
FROM python:3.11.4-slim-buster

COPY requirements.txt .

RUN pip install --user -r requirements.txt
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1pu

COPY . .

CMD ["python3", "voyage_bot/bot.py"]
FROM python:3.11.3-alpine3.18

COPY . .

RUN pip install -r requirements.txt

RUN mkdir /content

RUN crontab crontab

CMD ["crond", "-f"]
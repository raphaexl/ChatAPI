FROM python:3.10.4

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . /app
RUN ["chmod", "+x", "/app/run_django.sh"]
CMD ["/app/run_django.sh"]

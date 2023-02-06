FROM python:3.8-slim


RUN mkdir /app


#COPY requirements.txt /app
COPY ["requirements.txt", "/app"]

RUN python3 -m pip install --upgrade pip
RUN pip3 install -r /app/requirements.txt --no-cache-dir

#COPY ./ /app
COPY ["./", "/app"]

WORKDIR /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
# CMD ["python3", "manage.py", "runserver", "0:8000"]

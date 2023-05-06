FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "backend/manage.py", "runserver", "0.0.0.0:8000"]


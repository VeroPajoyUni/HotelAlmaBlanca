FROM python:3.12

WORKDIR /app

COPY habitaciones_requirements.txt .
RUN pip install -r habitaciones_requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "habitaciones_app.py"]

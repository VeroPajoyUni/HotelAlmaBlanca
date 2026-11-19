FROM python:3.12

WORKDIR /app

COPY notificaciones_requirements.txt .
RUN pip install -r notificaciones_requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "notificaciones_app.py"]

FROM python:3.12

WORKDIR /app

COPY reservas_requirements.txt .
RUN pip install -r reservas_requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "reservas_app.py"]

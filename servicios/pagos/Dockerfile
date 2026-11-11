
FROM python:3.12

WORKDIR /app

COPY pagos_requirements.txt .
RUN pip install -r pagos_requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "pagos_app.py"]

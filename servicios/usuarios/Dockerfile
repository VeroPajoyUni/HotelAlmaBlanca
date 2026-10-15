FROM python:3.12

WORKDIR /app

COPY usuarios_requirements.txt .
RUN pip install -r usuarios_requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "usuarios_app.py"]

FROM python:3.11-slim

WORKDIR /app

COPY alert-manager/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alert-manager/ .

CMD ["python", "main.py"]

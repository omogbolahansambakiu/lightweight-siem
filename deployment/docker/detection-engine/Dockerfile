FROM python:3.11-slim

WORKDIR /app

COPY detection-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY detection-engine/ .
COPY config/ /app/config/
COPY rules/ /app/rules/

CMD ["python", "main.py"]

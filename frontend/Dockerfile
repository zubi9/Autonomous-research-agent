FROM python:3.12-slim

WORKDIR /app

COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ ./frontend/

CMD ["sh", "-c", "streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=${PORT}"]
#!/bin/bash
set -e

echo "Starting services..."

# Start Streamlit in background
echo "Starting Streamlit on port 8501..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 --logger.level=info &
STREAMLIT_PID=$!

# Start FastAPI (foreground)
echo "Starting FastAPI on port ${PORT:-8000}..."
uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}

# Cleanup: if FastAPI exits, kill Streamlit
kill $STREAMLIT_PID 2>/dev/null || true

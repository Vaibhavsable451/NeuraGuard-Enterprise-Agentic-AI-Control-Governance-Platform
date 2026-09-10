#!/bin/bash
# AWS EC2 Startup Script for NeuraGuard Platform
# Starts both FastAPI Backend (Port 8000) and Streamlit Frontend (Port 8501) in background.

set -e

# Create virtual environment if it doesn't exist
if [ ! -x ".venv/bin/python" ]; then
  sudo apt-get update
  sudo apt-get install -y python3-venv
  python3 -m venv .venv
fi

echo "Installing requirements inside .venv..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "Starting FastAPI Backend on port 8000..."
pkill -f '[u]vicorn app.api.main:app' || true
nohup .venv/bin/uvicorn app.api.main:app --host 0.0.0.0 --port 8000 > logs_api.log 2>&1 &

echo "Starting Streamlit UI on port 8501..."
pkill -f '[s]treamlit run' || true
nohup .venv/bin/streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0 > logs_streamlit.log 2>&1 &

echo "NeuraGuard Platform background services started successfully!"



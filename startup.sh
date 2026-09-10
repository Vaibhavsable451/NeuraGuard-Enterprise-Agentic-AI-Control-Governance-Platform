#!/bin/bash
# Azure App Service startup command for the FastAPI backend (no Docker).
# Configure this as the "Startup Command" in Azure App Service > Configuration.
pip install -r requirements.txt
uvicorn app.api.main:app --host 0.0.0.0 --port 8000

#!/bin/bash
# Azure App Service startup command for the Streamlit frontend (no Docker).
pip install -r requirements.txt
streamlit run streamlit_app/app.py --server.port 8000 --server.address 0.0.0.0

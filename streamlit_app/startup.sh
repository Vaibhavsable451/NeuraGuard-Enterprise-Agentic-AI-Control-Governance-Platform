#!/bin/bash
# AWS EC2 startup command for the Streamlit frontend.
pip install -r requirements.txt
streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0


#!/bin/bash

# Start backend in the background
# backend.main:app is correct
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start frontend in the foreground
# Streamlit configuration is now handled by env vars in Dockerfile but we enforce it here to be safe
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

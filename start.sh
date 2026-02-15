#!/bin/bash

# Start backend in the foreground
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

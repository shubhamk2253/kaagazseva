# KaagazSeva Backend

Enterprise-grade document service processing platform.

## Setup

1. Create virtual environment
   python -m venv venv

2. Activate
   source venv/bin/activate   (Linux/Mac)
   venv\Scripts\activate      (Windows)

3. Install dependencies
   pip install -r requirements.txt

4. Create .env file (see example)

5. Run server
   python app.py

## Structure

routes/        -> API endpoints  
services/      -> business logic  
models/        -> DB layer  
uploads/       -> uploaded documents  

## Production Run
gunicorn app:app


# 1. Start from a small Linux that already has Python 3.12 installed
FROM python:3.12-slim

# 2. Work inside the /app folder in the container
WORKDIR /app

# 3. Copy the shopping list first and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the code (app.py, templates)
COPY . .

# 5. The app listens on port 8000
EXPOSE 8000

# 6. Start the app with gunicorn (2 workers)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
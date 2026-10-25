FROM python:3.12-slim

WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Uvicorn will run on
EXPOSE 8000

# Start the FastAPI server binding to 0.0.0.0 for external access
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
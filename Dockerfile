# Base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot script
COPY bot.py .

# Expose port (optional, helpful for dev tools or health checks)
EXPOSE 8080

# Run bot
CMD ["python", "bot.py"]

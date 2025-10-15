# Use official Python image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory in container
WORKDIR /app

# Copy Docker requirements
COPY requirements-docker.txt .

# Install dependencies using the Docker-specific file
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements-docker.txt

# Copy the full project
COPY . .

# Set default command to run your main script
CMD ["python", "-m", "MedicalAgent.main"]

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_ROOT_USER_ACTION=ignore

# Set working directory
WORKDIR /app

# Install system dependencies (only what’s needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage caching
COPY requirements/ requirements/

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements/development.txt

# Copy the rest of the project
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to start server
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi.application"]
CMD ["python", "manage.py", "runserver"]

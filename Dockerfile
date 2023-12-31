# Start from an official Python runtime as the base image
FROM python:3.8-slim

# Install necessary system dependencies
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends curl build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install poetry

# Set environment variables for Poetry
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files into the container for dependency installation
COPY pyproject.toml poetry.lock ./

# Install the project's dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy the rest of the application's files into the container
COPY . .

# Specify the command to run your application
CMD ["python", "run.py"]

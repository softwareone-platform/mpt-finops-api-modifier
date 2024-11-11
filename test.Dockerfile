# Use an official Python runtime as a parent image
FROM python:3.12.2-bookworm
ENV PYTHONUNBUFFERED=1 POETRY_VERSION=1.7.0

RUN pip3 install poetry==$POETRY_VERSION

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.4.2 \
    DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy Poetry files and install dependencies
COPY pyproject.toml poetry.lock ./
#RUN poetry install --no-root --no-interaction --no-ansi
RUN poetry update && poetry install --with dev

# Copy the rest of the application code and tests into the container
COPY . /app

# Set environment variable for locating test data in conftest.py
ENV PYTEST_CURRENT_TEST=/app/tests

# Run tests using Poetry to handle the virtual environment
CMD ["poetry", "run", "pytest", "--disable-warnings", "-v"]

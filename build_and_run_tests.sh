#!/bin/bash

# Variables
DOCKERFILE="test.Dockerfile"
IMAGE_NAME="optscale_api_modifier_test"

# Build the Docker image
echo "Building Docker image..."
docker build -f "$DOCKERFILE" -t "$IMAGE_NAME" .

if [ $? -ne 0 ]; then
  echo "Error: Docker build failed!"
  exit 1
fi

echo "Docker image built successfully: $IMAGE_NAME"

# Run the Docker container
echo "Running Docker container..."
docker run --rm "$IMAGE_NAME"

if [ $? -ne 0 ]; then
  echo "Error: Docker run failed!"
  exit 1
fi

echo "Docker container ran successfully."

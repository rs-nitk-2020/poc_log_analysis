#!/bin/bash

IMAGE_NAME="jokesta/warning"
CONTAINER_NAME="app1"

# Get local image digest
LOCAL_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' $IMAGE_NAME 2>/dev/null)

# Pull the latest image
docker pull $IMAGE_NAME > /dev/null

# Get new image digest
NEW_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' $IMAGE_NAME 2>/dev/null)

# Check if digests are different
if [ "$LOCAL_DIGEST" != "$NEW_DIGEST" ]; then
    echo "New version available. Pulling the updated image..."
fi

RUNNING=$(docker inspect --format="{{.State.Running}}" $CONTAINER_NAME 2>/dev/null)
if [ "$RUNNING" == "true" ]; then
    echo "Container $CONTAINER_NAME is already running. Stopping and removing it..."
    docker stop $CONTAINER_NAME >/dev/null
    docker rm $CONTAINER_NAME >/dev/null
fi

# Run the container with the latest image
CONTAINER_ID=$(docker run -d --name $CONTAINER_NAME $IMAGE_NAME)
CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID)
echo "Service is running at: http://$CONTAINER_IP:8000"

#!/bin/bash

IMAGE_NAME="jokesta/warning"
CONTAINER_NAME="app1"

RUNNING=$(docker inspect --format="{{.State.Running}}" $CONTAINER_NAME 2>/dev/null)
if [ "$RUNNING" == "true" ]; then
    echo "Container $CONTAINER_NAME is already running. Stopping and removing it..."
    docker stop $CONTAINER_NAME >/dev/null
    docker rm $CONTAINER_NAME >/dev/null
    echo "Container $CONTAINER_NAME is stopped"
fi

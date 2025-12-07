#!/bin/bash
set -e

PROJECT_DIR=/srv/star-burger

cd "$PROJECT_DIR"

git pull origin main

docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

echo "Deployed!"

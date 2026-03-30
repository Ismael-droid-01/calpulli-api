#!/bin/bash 
PROFILE=${1:-"prod"}
echo "Deploying with profile: $PROFILE"
docker compose --profile $PROFILE --env-file .env.dev -f docker-compose.yml up -d --build 
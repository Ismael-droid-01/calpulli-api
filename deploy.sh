#!/bin/bash 
readonly PROFILE=${1:-"prod"}
readonly ENV_FILE=${2:-".env.dev"}
echo "Deploying with profile: $PROFILE"
docker compose --profile $PROFILE --env-file $ENV_FILE -f docker-compose.yml up -d --build 
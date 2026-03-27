#!/bin/bash 
docker compose --env-file .env.dev -f docker-compose.yml up -d --build 
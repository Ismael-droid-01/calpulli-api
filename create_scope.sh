#!/bin/bash
readonly scope=${1:-"calpulli"}

curl --request POST \
  --url http://localhost:10000/api/v4/scopes \
  --header 'Content-Type: application/json' \
  --data '{
  "name":"'"$scope"'"
}'

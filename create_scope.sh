#!/bin/bash
readonly scope=${1:-"calpulli"}
readonly ACCOUNT_ID="calpulli_ci"
curl --request POST \
  --url http://localhost:10000/api/v4/accounts/$ACCOUNT_ID/scopes \
  --header 'Content-Type: application/json' \
  --data '{
  "name":"'"$scope"'"
}'

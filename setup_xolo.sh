#!/bin/bash
set -e

XOLO_URL="http://localhost:10000"
ENV_FILE=".env.dev"
ADMIN_TOKEN="${X_ADMIN_TOKEN:-admin_token_here}"
ACCOUNT_ID="calpulli_ci"
# 1. Wait for the documentation page instead of /health
echo "Waiting for Xolo API to be ready..."
timeout 30s sh -c "until curl -s $XOLO_URL/docs > /dev/null; do sleep 1; done" || (echo "Xolo timed out" && exit 1)

# 2. Creating Account
echo "Creating Account..."
ACCOUNT_URL="$XOLO_URL/api/v4/accounts"

curl -s -X POST "$ACCOUNT_URL" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: $ADMIN_TOKEN" \
  -d "{\"account_id\": \"$ACCOUNT_ID\", \"name\": \"CI Test Account\"}"

echo -e "\nGenerating API Key..."
# 3. Generating API Key
# Note: Ensure "all" is a valid value in your APIKeyScope Enum
RESPONSE=$(curl -s -X POST "$ACCOUNT_URL/$ACCOUNT_ID/apikeys" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: $ADMIN_TOKEN" \
  -d '{
    "name": "ci_key", 
    "scopes": ["all"]
  }')

# 4. Extraction & Validation
API_KEY=$(echo "$RESPONSE" | jq -r '.key // empty')

if [ -z "$API_KEY" ] || [ "$API_KEY" == "null" ]; then
  echo "Error: Could not extract API Key."
  echo "Full response: $RESPONSE"
  # Check if the error is a 404 again
  if [[ "$RESPONSE" == *"Not Found"* ]]; then
    echo "Check if the route is actually mounted at $ACCOUNT_URL"
  fi
  exit 1
fi

# 5. Update .env.dev
echo "Updating $ENV_FILE..."
if grep -q "XOLO_API_KEY=" "$ENV_FILE"; then
  sed -i "s|^XOLO_API_KEY=.*|XOLO_API_KEY=$API_KEY|" "$ENV_FILE"
else
  echo "XOLO_API_KEY=$API_KEY" >> "$ENV_FILE"
fi

# 6. Export for GitHub Actions
if [ -n "$GITHUB_ENV" ]; then
  echo "XOLO_API_KEY=$API_KEY" >> $GITHUB_ENV
  echo "XOLO_ACCOUNT_ID=$ACCOUNT_ID" >> $GITHUB_ENV
  
  echo "::add-mask::$API_KEY"

  echo 
fi

echo "Success: XOLO_API_KEY set in $ENV_FILE"



echo "Verifying API Keys for account: $ACCOUNT_ID..."
# This hits the GET /api/v4/accounts/{id}/apikeys endpoint
METADATA_RESPONSE=$(curl -s -X GET "$XOLO_URL/api/v4/accounts/$ACCOUNT_ID/apikeys" \
  -H "X-Admin-Token: $ADMIN_TOKEN")

echo "Registered Key Metadata:"
echo "$METADATA_RESPONSE" | jq '.'

# Optional: Verify the key we just created is in the list
FOUND=$(echo "$METADATA_RESPONSE" | jq -r ".[] | select(.name == \"ci_key\") | .key_id")

if [ -n "$FOUND" ]; then
  echo "Verification Success: Key '$FOUND' is active."
else
  echo "Verification Warning: Key not found in metadata list."
fi


#  Create Scope
curl --request POST \
  --url http://localhost:10000/api/v4/accounts/$ACCOUNT_ID/scopes \
  --header 'Content-Type: application/json' \
  --header "X-Admin-Token: $ADMIN_TOKEN" \
  --data '{
  "name":"'"$scope"'"
}'

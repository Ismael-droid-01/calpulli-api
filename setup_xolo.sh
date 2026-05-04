#!/bin/bash
set -e

XOLO_URL="http://localhost:10000"
ENV_FILE=".env.dev"
# Use a default if the secret isn't passed for local testing
ADMIN_TOKEN="${X_ADMIN_TOKEN:-admin_token_here}"

echo "Waiting for Xolo API to be ready..."
timeout 30s sh -c "until curl -s $XOLO_URL/docs; do sleep 1; done" || (echo "Xolo timed out" && exit 1)

echo "Creating Account..."
# Matches CreateAccountDTO(account_id: str, name: str)
curl -s -X POST "$XOLO_URL/api/v4/accounts" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: $ADMIN_TOKEN" \
  -d '{"account_id": "calpulli_ci", "name": "CI Test Account"}'

echo "Generating API Key..."
# Matches CreateAPIKeyDTO(name: str, scopes: list[APIKeyScope])
# Note: Adjust "all" to your specific Enum value
RESPONSE=$(curl -s -X POST "$XOLO_URL/api/v4/accounts/calpulli_ci/apikeys" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: $ADMIN_TOKEN" \
  -d '{"name": "ci_key", "scopes": ["all"]}')

# Extract 'key' from CreatedAPIKeyResponseDTO
API_KEY=$(echo "$RESPONSE" | jq -r '.key')

if [ "$API_KEY" == "null" ] || [ -z "$API_KEY" ]; then
  echo "Error: API Key is empty. Full response: $RESPONSE"
  exit 1
fi

echo "Updating $ENV_FILE..."
# Replace existing XOLO_API_KEY or append if missing
if grep -q "XOLO_API_KEY=" "$ENV_FILE"; then
  sed -i "s|^XOLO_API_KEY=.*|XOLO_API_KEY=$API_KEY|" "$ENV_FILE"
else
  echo "XOLO_API_KEY=$API_KEY" >> "$ENV_FILE"
fi

# Export for the current GitHub Action runner process
echo "XOLO_API_KEY=$API_KEY" >> $GITHUB_ENV
echo "::add-mask::$API_KEY"
echo "Success: Environment updated."
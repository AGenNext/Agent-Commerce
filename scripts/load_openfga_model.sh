#!/usr/bin/env bash
# Create an OpenFGA store and load the ecosystem authorization model.
#
# Usage:
#   OPENFGA_API_URL=http://localhost:8081 ./scripts/load_openfga_model.sh
#
# Prints the store id and authorization model id to set as
# OPENFGA_STORE_ID / OPENFGA_MODEL_ID for agent-api.
#
# Requires the FGA CLI (https://github.com/openfga/cli). Without it, use the
# OpenFGA Playground at http://localhost:3000 or the /stores HTTP API directly.
set -euo pipefail

API_URL="${OPENFGA_API_URL:-http://localhost:8081}"
MODEL_FILE="$(dirname "$0")/../authz/model.fga"

if ! command -v fga >/dev/null 2>&1; then
  echo "FGA CLI not found. Install it: https://github.com/openfga/cli" >&2
  echo "Then re-run, or load authz/model.fga via the Playground ($API_URL/playground)." >&2
  exit 1
fi

export FGA_API_URL="$API_URL"

echo "Creating store..."
STORE_ID="$(fga store create --name agent-commerce --model "$MODEL_FILE" | python3 -c 'import sys,json;print(json.load(sys.stdin)["store"]["id"])')"
echo "OPENFGA_STORE_ID=$STORE_ID"

MODEL_ID="$(fga model list --store-id "$STORE_ID" | python3 -c 'import sys,json;print(json.load(sys.stdin)["authorization_models"][0]["id"])')"
echo "OPENFGA_MODEL_ID=$MODEL_ID"

echo
echo "Export these for agent-api:"
echo "  export OPENFGA_ENABLED=true"
echo "  export OPENFGA_API_URL=$API_URL"
echo "  export OPENFGA_STORE_ID=$STORE_ID"
echo "  export OPENFGA_MODEL_ID=$MODEL_ID"

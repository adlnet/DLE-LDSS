#!/usr/bin/env bash

### this script requires the file to be executable
### if this is your first time cloning, do that with: 
### chmod +x start.sh

set -euo pipefail

DOCKER_CFG="${HOME}/.docker/config.json"
REG="registry1.dso.mil"

# Check if we already have an entry for registry1.dso.mil
if [[ -f "$DOCKER_CFG" ]] && grep -q "\"$REG\"" "$DOCKER_CFG"; then
  echo "Already logged in to $REG"
else
  # If not, prompt for Harbor username & secret
  read -p "Harbor username: " HARBOR_USER
  read -s -p "Harbor CLI Secret: " HARBOR_SECRET
  echo

  # Perform the login
  echo "$HARBOR_SECRET" | docker login "$REG" \
    --username "$HARBOR_USER" \
    --password-stdin
  echo "Login succeeded"
fi

# Choose environment
echo
echo "Select environment:"
echo "  p) Production (docker-compose.yml)"
echo "  d) Development  (docker-compose.dev.yml)"
read -p "Enter [p/d] (default: p): " MODE
MODE=${MODE:-p}

case "$MODE" in
  p|P)
    COMPOSE_FILE="docker-compose.yaml"
    ;;
  d|D)
    COMPOSE_FILE="docker-compose.dev.yaml"
    ;;
  *)
    echo "Invalid choice: $MODE"
    exit 1
    ;;
esac

# Run service
echo
echo "Using '$COMPOSE_FILE' docker-compose up --build"
docker-compose -f "$COMPOSE_FILE" up --build
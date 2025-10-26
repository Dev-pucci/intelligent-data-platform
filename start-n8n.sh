#!/bin/bash

echo "Starting n8n workflow automation..."
echo ""

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start n8n
echo "n8n will be available at: http://localhost:5678"
echo ""
npx n8n start

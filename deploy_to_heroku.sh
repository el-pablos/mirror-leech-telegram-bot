#!/bin/bash

# Heroku Deployment Script for Mirror-Leech Telegram Bot
# This script automates the Heroku deployment process

set -e

echo "========================================="
echo "Heroku Deployment Script"
echo "Mirror-Leech Telegram Bot"
echo "========================================="

# Configuration
HEROKU_API_KEY="${HEROKU_API_KEY:-YOUR_HEROKU_API_KEY_HERE}"
APP_NAME="${1:-mirror-leech-bot-$(date +%s)}"
REGION="us"
STACK="container"
REPO_URL="https://github.com/el-pablos/mirror-leech-telegram-bot"
BRANCH="heroku"

echo "App Name: $APP_NAME"
echo "Region: $REGION"
echo "Stack: $STACK"
echo "Repository: $REPO_URL"
echo "Branch: $BRANCH"
echo "========================================="

# Function to make Heroku API calls
heroku_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -z "$data" ]; then
        curl -s -X "$method" \
            -H "Authorization: Bearer $HEROKU_API_KEY" \
            -H "Accept: application/vnd.heroku+json; version=3" \
            -H "Content-Type: application/json" \
            "https://api.heroku.com$endpoint"
    else
        curl -s -X "$method" \
            -H "Authorization: Bearer $HEROKU_API_KEY" \
            -H "Accept: application/vnd.heroku+json; version=3" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "https://api.heroku.com$endpoint"
    fi
}

# Step 1: Create Heroku App
echo ""
echo "Step 1: Creating Heroku app..."
CREATE_RESPONSE=$(heroku_api POST "/apps" "{\"name\":\"$APP_NAME\",\"region\":\"$REGION\",\"stack\":\"$STACK\"}")

if echo "$CREATE_RESPONSE" | grep -q "\"id\""; then
    echo "✓ App created successfully!"
    APP_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    WEB_URL=$(echo "$CREATE_RESPONSE" | grep -o '"web_url":"[^"]*"' | cut -d'"' -f4)
    GIT_URL=$(echo "$CREATE_RESPONSE" | grep -o '"git_url":"[^"]*"' | cut -d'"' -f4)
    
    echo "  App ID: $APP_ID"
    echo "  Web URL: $WEB_URL"
    echo "  Git URL: $GIT_URL"
else
    echo "✗ Failed to create app!"
    echo "Response: $CREATE_RESPONSE"
    exit 1
fi

# Step 2: Set Stack to Container
echo ""
echo "Step 2: Setting stack to container..."
STACK_RESPONSE=$(heroku_api PATCH "/apps/$APP_NAME" "{\"build_stack\":\"$STACK\"}")
echo "✓ Stack set to container"

# Step 3: Add GitHub Integration (if possible)
echo ""
echo "Step 3: GitHub integration..."
echo "Note: GitHub integration requires OAuth, which cannot be automated via API."
echo "You'll need to connect GitHub manually via Heroku Dashboard."

# Step 4: Create Formation (Worker Dyno)
echo ""
echo "Step 4: Configuring dyno formation..."
FORMATION_RESPONSE=$(heroku_api PATCH "/apps/$APP_NAME/formation" "[{\"type\":\"worker\",\"quantity\":1,\"size\":\"eco\"}]")
echo "✓ Worker dyno configured (Eco type)"

# Step 5: Display Next Steps
echo ""
echo "========================================="
echo "Heroku App Created Successfully!"
echo "========================================="
echo ""
echo "App Details:"
echo "  Name: $APP_NAME"
echo "  URL: $WEB_URL"
echo "  Git URL: $GIT_URL"
echo ""
echo "Next Steps:"
echo ""
echo "1. Add Heroku remote to your git repository:"
echo "   git remote add heroku $GIT_URL"
echo ""
echo "2. Deploy the heroku branch:"
echo "   git push heroku heroku:main"
echo ""
echo "3. Scale the worker dyno:"
echo "   heroku ps:scale worker=1 -a $APP_NAME"
echo ""
echo "4. Check logs:"
echo "   heroku logs --tail -a $APP_NAME"
echo ""
echo "5. Or connect GitHub via Dashboard:"
echo "   https://dashboard.heroku.com/apps/$APP_NAME/deploy/github"
echo ""
echo "========================================="
echo "Deployment script completed!"
echo "========================================="


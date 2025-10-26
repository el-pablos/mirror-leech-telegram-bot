#!/bin/bash

# Render.com optimized startup script for Mirror-Leech Telegram Bot
# This script handles Render-specific configurations and environment setup

echo "========================================="
echo "Starting Mirror-Leech Telegram Bot"
echo "Platform: Render.com"
echo "========================================="

# Activate virtual environment
source mltbenv/bin/activate

# Display environment info
echo "Python version: $(python3 --version)"
echo "Working directory: $(pwd)"

# Check if PORT is set (Render.com sets this)
if [ -n "$PORT" ]; then
    echo "Render PORT detected: $PORT"
    export BASE_URL_PORT=$PORT
else
    echo "No PORT environment variable found, using default"
fi

# Display key configuration (without sensitive data)
echo "========================================="
echo "Configuration Check:"
echo "========================================="
if [ -n "$BOT_TOKEN" ]; then
    echo "✓ BOT_TOKEN is set"
else
    echo "✗ BOT_TOKEN is missing!"
fi

if [ -n "$OWNER_ID" ]; then
    echo "✓ OWNER_ID is set"
else
    echo "✗ OWNER_ID is missing!"
fi

if [ -n "$TELEGRAM_API" ]; then
    echo "✓ TELEGRAM_API is set"
else
    echo "✗ TELEGRAM_API is missing!"
fi

if [ -n "$TELEGRAM_HASH" ]; then
    echo "✓ TELEGRAM_HASH is set"
else
    echo "✗ TELEGRAM_HASH is missing!"
fi

if [ -n "$DATABASE_URL" ]; then
    echo "✓ DATABASE_URL is set"
else
    echo "⚠ DATABASE_URL is not set (optional but recommended)"
fi

echo "========================================="

# Run update script to pull latest changes from upstream
echo "Running update script..."
python3 update.py

# Check if update was successful
if [ $? -ne 0 ]; then
    echo "⚠ Update script encountered issues, continuing anyway..."
fi

# Start the bot
echo "========================================="
echo "Starting bot application..."
echo "========================================="
python3 -m bot

# If bot exits, show exit code
EXIT_CODE=$?
echo "========================================="
echo "Bot exited with code: $EXIT_CODE"
echo "========================================="
exit $EXIT_CODE


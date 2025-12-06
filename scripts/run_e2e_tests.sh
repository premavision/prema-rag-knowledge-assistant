#!/bin/bash
# Script to run e2e tests with proper setup

set -e

echo "🚀 Running E2E Tests for Prema RAG Knowledge Assistant"
echo "======================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Make sure OPENAI_API_KEY is set."
fi

# Check if Playwright browsers are installed
echo "📦 Checking Playwright browsers..."
if ! python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().chromium.launch()" 2>/dev/null; then
    echo "📥 Installing Playwright browsers..."
    playwright install chromium
fi

# Run tests
echo ""
echo "🧪 Running e2e tests..."
echo ""

pytest tests/e2e/ -v "$@"

echo ""
echo "✅ E2E tests completed!"

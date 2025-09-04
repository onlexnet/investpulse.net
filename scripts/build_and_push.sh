#!/bin/bash

# Build and Prepare Static Assets for InvestPulse
# Usage: ./scripts/build_and_push.sh [environment]
# Example: ./scripts/build_and_push.sh dev

set -euo pipefail

# Configuration
ENVIRONMENT=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WEBAPP_DIR="$REPO_ROOT/webapp"
BUILD_OUTPUT="$WEBAPP_DIR/out"

echo "🏗️  Building static assets for environment: $ENVIRONMENT"
echo "📁 Webapp directory: $WEBAPP_DIR"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^[a-z0-9-]+$ ]]; then
  echo "❌ Error: Environment name must contain only lowercase letters, numbers, and hyphens"
  exit 1
fi

# Change to webapp directory
cd "$WEBAPP_DIR"

# Check if package.json exists
if [ ! -f "package.json" ]; then
  echo "❌ Error: package.json not found in $WEBAPP_DIR"
  exit 1
fi

echo "📦 Installing dependencies..."
npm ci

echo "🧹 Cleaning previous build..."
rm -rf "$BUILD_OUTPUT"

echo "🔍 Running linting..."
npm run lint

echo "🔨 Building static application..."
NODE_ENV="$ENVIRONMENT" npm run build:static

# Verify build output
if [ ! -d "$BUILD_OUTPUT" ]; then
  echo "❌ Error: Build output directory not found at $BUILD_OUTPUT"
  exit 1
fi

echo "📊 Build statistics:"
echo "   Output directory: $BUILD_OUTPUT"
echo "   Files created: $(find "$BUILD_OUTPUT" -type f | wc -l)"
echo "   Total size: $(du -sh "$BUILD_OUTPUT" | cut -f1)"

echo "✅ Build completed successfully!"
echo "📋 Next steps:"
echo "   1. Static files are ready in: $BUILD_OUTPUT"
echo "   2. Deploy using: ./scripts/deploy.sh $ENVIRONMENT"
echo "   3. Or deploy via GitHub Actions to Azure Static Web Apps"
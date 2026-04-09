#!/bin/bash
set -e

echo ""
echo "🚀 LinkedIn AI Agent"
echo "──────────────────────────────────"

# Check .env exists
if [ ! -f ".env" ]; then
  echo "❌ .env file not found."
  echo "   Copy .env.example to .env and fill in your values."
  echo "   Run: cp .env.example .env"
  exit 1
fi

# Check Python is available
if ! command -v python3 &> /dev/null; then
  echo "❌ Python 3 is required but not found."
  exit 1
fi

python3 main.py

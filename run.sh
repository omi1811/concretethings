#!/bin/bash
# Quick start script for ConcreteThings application

echo "🏗️  ConcreteThings - Mix Design Management"
echo "=========================================="
echo ""

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt -q
    echo "✓ Dependencies installed"
    echo ""
fi

# Check if database has data
RECORD_COUNT=$(python -c "from server.db import session_scope; from server.models import MixDesign; \
with session_scope() as s: print(s.query(MixDesign).count())" 2>/dev/null)

if [ "$RECORD_COUNT" = "0" ]; then
    echo "🌱 Seeding sample data..."
    python seed.py
    echo ""
fi

echo "🚀 Starting Flask server..."
echo "   URL: http://localhost:8000"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

# Start the server
python -m server.app

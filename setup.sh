#!/bin/bash

echo "===================================="
echo "BaseAgent Setup Script"
echo "===================================="
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  Please edit .env file and add your OPENAI_API_KEY"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "===================================="
echo "Setup Complete!"
echo "===================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OPENAI_API_KEY"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run examples:"
echo "   - python example_mcp.py"
echo "   - python example_usage.py"
echo "   - python server.py (to start API server)"
echo ""

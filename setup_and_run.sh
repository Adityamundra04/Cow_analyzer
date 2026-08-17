#!/bin/bash

echo "========================================"
echo "Cow Farm Analytics - Easy Setup"
echo "========================================"
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "Virtual environment found. Activating..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment."
        echo "Please make sure Python 3 is installed."
        exit 1
    fi
    source venv/bin/activate
    
    echo "Installing required packages..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install packages."
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "Starting Cow Farm Analytics App..."
echo "========================================"
echo ""
echo "The app will open in your browser at:"
echo "http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

python app.py

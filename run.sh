#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Check if a parameter is provided
if [ -z "$1" ]; then
    echo "Usage: $0 \"example string here\""
    deactivate
    exit 1
fi

# Run the Python script with the provided parameter
python app.py "$1"

# Deactivate the virtual environment
deactivate
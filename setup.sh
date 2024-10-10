#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Notify user
echo "Virtual environment created and dependencies installed!"
echo "You can run the script now using: ./run.sh \"example query here\""

# Leave virtual env
deactivate
#!/bin/bash
set -e

echo "Starting SmartMarket..."

# 1) Start server in Docker
docker-compose up -d --build

# 2) Install client dependencies if needed
cd client
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# 3) Run client
python main.py

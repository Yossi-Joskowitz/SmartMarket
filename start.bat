@echo off
echo Starting SmartMarket...

:: 1) Start server in Docker
docker-compose up -d --build
if %errorlevel% neq 0 (
    echo Docker failed. Is Docker Desktop running?
    pause
    exit /b 1
)

:: 2) Install client dependencies if needed
cd client
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -q -r requirements.txt

:: 3) Run client
python main.py

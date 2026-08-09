#!/bin/bash

# DesignBook Unified Startup Script
# This script orchestrates the backend and frontend services.

# Colors for logging
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Cleanup function — ensures child processes are killed on exit
cleanup() {
  echo -e "\n${RED}>>> Shutting down DesignBook services...${NC}"
  [[ -n "$BACKEND_PID" ]] && kill "$BACKEND_PID" 2>/dev/null
  [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null
  wait 2>/dev/null
  echo -e "${GREEN}>>> All services stopped.${NC}"
}
trap cleanup EXIT INT TERM

echo -e "${BLUE}>>> Starting DesignBook Services...${NC}"

# 1. Verify System Services
echo -e "${BLUE}>>> Checking PostgreSQL and Redis status...${NC}"
pg_isready -q || { echo -e "${RED}PostgreSQL is not running. Please start it with 'sudo service postgresql start'${NC}"; exit 1; }
redis-cli ping > /dev/null 2>&1 || { echo -e "${RED}Redis is not running. Please start it with 'sudo service redis-server start'${NC}"; exit 1; }
echo -e "${GREEN}>>> PostgreSQL and Redis are running.${NC}"

# 2. Setup Environment
export PYTHONPATH=$PYTHONPATH:$(pwd)/app
cd app

# Ensure .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found in app directory.${NC}"
    exit 1
fi

# 3. Start Backend (background)
echo -e "${BLUE}>>> Launching Backend (Uvicorn on :8000)...${NC}"
./.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# 4. Start Frontend (background)
echo -e "${BLUE}>>> Launching Frontend (Vite on :5173)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}>>> DesignBook is running. Press Ctrl+C to stop all services.${NC}"

# Wait for both processes
wait

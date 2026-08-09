#!/bin/bash

# setup_db.sh - DesignBook Database Initialization Script
# This script initializes the PostgreSQL database and user.
# Safe to run multiple times — uses IF NOT EXISTS to avoid crashes.

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}>>> Initializing DesignBook Database...${NC}"

# Create database user (idempotent)
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='designbook'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE USER designbook WITH PASSWORD 'designbook';"

# Create database (idempotent)
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='designbook'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE DATABASE designbook OWNER designbook;"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE designbook TO designbook;"

echo -e "${GREEN}>>> Database initialization complete.${NC}"
echo -e ">>> User: designbook"
echo -e ">>> Database: designbook"

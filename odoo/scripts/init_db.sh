#!/bin/bash
# Odoo Database Initialization Script

set -e

echo "====================================="
echo "Odoo Database Initialization"
echo "====================================="
echo ""

# Configuration
DB_NAME="ai_employee"
ADMIN_PASSWORD="admin123"
EMAIL="admin@example.com"
PASSWORD="admin"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if Odoo containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠ Odoo containers are not running. Starting them...${NC}"
    docker-compose up -d
    
    echo -e "${YELLOW}Waiting for Odoo to be ready...${NC}"
    sleep 30
fi

# Check if Odoo is responding
echo -e "${YELLOW}Checking if Odoo is responding...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8069 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Odoo is responding${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 5
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Odoo did not start within expected time${NC}"
    echo "  Check logs: docker-compose logs odoo"
    exit 1
fi

# Create database
echo ""
echo -e "${YELLOW}Creating database: $DB_NAME${NC}"

RESPONSE=$(curl -s -X POST http://localhost:8069/web/database/create \
  -H "Content-Type: application/json" \
  -d "{
    \"master_pwd\": \"$ADMIN_PASSWORD\",
    \"name\": \"$DB_NAME\",
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"lang\": \"en_US\",
    \"phone\": \"\"
  }")

if echo "$RESPONSE" | grep -q "result"; then
    echo -e "${GREEN}✓ Database created successfully${NC}"
else
    echo -e "${YELLOW}⚠ Database may already exist or creation failed${NC}"
    echo "  Response: $RESPONSE"
fi

echo ""
echo "====================================="
echo -e "${GREEN}Initialization Complete!${NC}"
echo "====================================="
echo ""
echo "Next Steps:"
echo "1. Open http://localhost:8069"
echo "2. Login with:"
echo "   Email: $EMAIL"
echo "   Password: $PASSWORD"
echo "3. Install Accounting module"
echo "4. Configure your company"
echo "5. Set up bank accounts"
echo ""
echo "Then test AI Employee integration:"
echo "  cd .."
echo "  python watchers/odoo_accounting.py --test"
echo ""

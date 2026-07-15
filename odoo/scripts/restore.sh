#!/bin/bash
# Odoo Database Restore Script

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "====================================="
echo "Odoo Database Restore"
echo "====================================="
echo ""

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}✗ Usage: $0 <backup_file>${NC}"
    echo ""
    echo "Available backups:"
    ls -lh "$(dirname "$0")/../backups/"*.sql* 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"
DB_NAME="ai_employee"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}✗ Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Confirm restore
echo -e "${YELLOW}⚠ WARNING: This will overwrite the existing database!${NC}"
echo ""
echo "Backup file: $BACKUP_FILE"
echo "Database: $DB_NAME"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 1
fi

# Check if database container is running
if ! docker ps | grep -q "odoo-db"; then
    echo -e "${RED}✗ Database container is not running${NC}"
    echo "  Start it with: docker-compose up -d"
    exit 1
fi

# Drop existing database
echo -e "${YELLOW}Dropping existing database...${NC}"
docker exec odoo-db dropdb -U odoo --if-exists "$DB_NAME" 2>/dev/null || true

# Create new database
echo -e "${YELLOW}Creating new database...${NC}"
docker exec odoo-db createdb -U odoo "$DB_NAME" 2>/dev/null || {
    echo -e "${RED}✗ Failed to create database${NC}"
    exit 1
}

# Restore backup
echo -e "${YELLOW}Restoring backup...${NC}"

if [[ "$BACKUP_FILE" == *.dump ]]; then
    # Binary dump restore
    docker cp "$BACKUP_FILE" odoo-db:/tmp/restore.dump
    docker exec odoo-db pg_restore -U odoo -d "$DB_NAME" --clean /tmp/restore.dump 2>/dev/null || {
        echo -e "${RED}✗ Restore failed${NC}"
        docker exec odoo-db rm -f /tmp/restore.dump
        exit 1
    }
    docker exec odoo-db rm -f /tmp/restore.dump
else
    # SQL dump restore
    docker cp "$BACKUP_FILE" odoo-db:/tmp/restore.sql
    docker exec odoo-db psql -U odoo -d "$DB_NAME" -f /tmp/restore.sql 2>/dev/null || {
        echo -e "${RED}✗ Restore failed${NC}"
        docker exec odoo-db rm -f /tmp/restore.sql
        exit 1
    }
    docker exec odoo-db rm -f /tmp/restore.sql
fi

echo ""
echo "====================================="
echo -e "${GREEN}Restore Complete!${NC}"
echo "====================================="
echo ""
echo "Database restored from: $BACKUP_FILE"
echo ""
echo "Next steps:"
echo "1. Restart Odoo container: docker-compose restart odoo"
echo "2. Open http://localhost:8069"
echo "3. Login with your credentials"
echo ""

#!/bin/bash
# Odoo Database Backup Script

set -e

BACKUP_DIR="$(dirname "$0")/../backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="ai_employee"
BACKUP_FILE="$BACKUP_DIR/odoo_backup_$TIMESTAMP.sql"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "====================================="
echo "Odoo Database Backup"
echo "====================================="
echo ""

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}Creating backup directory...${NC}"
    mkdir -p "$BACKUP_DIR"
fi

# Check if database container is running
if ! docker ps | grep -q "odoo-db"; then
    echo -e "${RED}✗ Database container is not running${NC}"
    exit 1
fi

# Create backup
echo -e "${YELLOW}Creating database backup...${NC}"
docker exec odoo-db pg_dump -U odoo -F c -f /tmp/backup.dump "$DB_NAME" 2>/dev/null || {
    echo -e "${YELLOW}⚠ Binary dump failed, trying SQL dump...${NC}"
    docker exec odoo-db pg_dump -U odoo "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null || {
        echo -e "${RED}✗ Backup failed${NC}"
        exit 1
    }
}

# Copy binary dump if created
if docker exec odoo-db test -f /tmp/backup.dump; then
    docker cp odoo-db:/tmp/backup.dump "$BACKUP_FILE.dump"
    echo -e "${GREEN}✓ Binary backup created: $BACKUP_FILE.dump${NC}"
    
    # Clean up temp file
    docker exec odoo-db rm -f /tmp/backup.dump
fi

# Also backup Odoo file storage
echo -e "${YELLOW}Backing up Odoo file storage...${NC}"
FILES_BACKUP="$BACKUP_DIR/odoo_files_$TIMESTAMP.tar.gz"
docker run --rm --volumes-from odoo -v "$BACKUP_DIR:/backup" ubuntu \
    tar czf /backup/odoo_files_$TIMESTAMP.tar.gz /var/lib/odoo 2>/dev/null || {
    echo -e "${YELLOW}⚠ File backup skipped (container may not have tar)${NC}"
}

echo ""
echo "====================================="
echo -e "${GREEN}Backup Complete!${NC}"
echo "====================================="
echo ""
echo "Backup files:"
ls -lh "$BACKUP_DIR"/*"$TIMESTAMP"* 2>/dev/null || echo "  No files found"
echo ""
echo "To restore a backup:"
echo "  ./scripts/restore.sh $BACKUP_FILE"
echo ""

# Clean old backups (keep last 5)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/odoo_backup_*.sql* 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 5 ]; then
    echo -e "${YELLOW}Cleaning old backups (keeping last 5)...${NC}"
    ls -1t "$BACKUP_DIR"/odoo_backup_*.sql* | tail -n +6 | xargs rm -f
fi

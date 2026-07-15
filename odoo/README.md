# Odoo Community Edition - AI Employee Integration

## Overview

This folder contains the complete Odoo setup for the AI Employee project. Odoo Community Edition provides:
- **Accounting & Invoicing** - Automated invoice tracking and payment monitoring
- **Financial Reporting** - Revenue analytics and business intelligence
- **Bank Reconciliation** - Automatic transaction matching
- **CEO Briefing Data** - Revenue metrics for weekly business audits

---

## 📁 Folder Structure

```
odoo/
├── docker-compose.yml          # Docker Compose setup (PostgreSQL + Odoo)
├── odoo.conf                   # Odoo configuration file
├── README.md                   # This file
├── addons/                     # Custom Odoo modules (optional)
├── backups/                    # Database backups
└── scripts/
    ├── init_db.sh              # Database initialization script
    ├── backup.sh               # Backup script
    └── restore.sh              # Restore script
```

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 2GB RAM available
- Ports 8069 available

### Step 1: Start Odoo

```bash
# Navigate to odoo folder
cd odoo

# Start Odoo (first time will take a few minutes)
docker-compose up -d

# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f odoo
```

**Odoo will be available at:** `http://localhost:8069`

### Step 2: Initial Setup

1. **Open your browser** and go to `http://localhost:8069`

2. **Create Database:**
   - Master Password: `admin123` (from odoo.conf)
   - Database Name: `ai_employee`
   - Email: `your-email@example.com`
   - Password: `your-password`
   - Click "Create Database"

3. **Install Accounting Module:**
   - Go to **Apps**
   - Search for "Invoicing" or "Accounting"
   - Click **Install**

4. **Configure Company:**
   - Go to **Settings** → **Companies**
   - Update company name, currency, fiscal year
   - Set up chart of accounts

5. **Set Up Bank Accounts:**
   - Go to **Accounting** → **Configuration** → **Bank Accounts**
   - Add your business bank accounts

### Step 3: Configure AI Employee

The AI Employee integration is already configured in the parent directory:

```bash
# Go back to project root
cd ..

# Odoo config is already in odoo_config.json
# Test the connection:
python watchers/odoo_accounting.py --test
```

---

## 🔧 Configuration

### Odoo Configuration (odoo.conf)

Key settings in `odoo.conf`:

```ini
admin_passwd = admin123          # Master password for DB operations
db_host = odoo-db                # PostgreSQL host
db_port = 5432                   # PostgreSQL port
db_user = odoo                   # Database user
db_password = odoo123            # Database password
xmlrpc_port = 8069               # Odoo web interface port
```

### AI Employee Configuration (odoo_config.json)

Located in odoo folder: `odoo/odoo_config.json`

```json
{
  "url": "http://localhost:8069",
  "db": "ai_employee",
  "username": "your-email@example.com",
  "password": "your-password"
}
```

**Note:** This file is in `.gitignore` to protect your credentials.

---

## 📊 Integration with AI Employee

### Available Features

#### 1. Invoice Management
```bash
# Get all invoices
python odoo_accounting.py --summary --days 30

# Test connection
python odoo_accounting.py --test
```

#### 2. Financial Reporting
The AI Employee can:
- Retrieve outstanding invoices
- Monitor payment status
- Generate revenue reports
- Calculate account balances

#### 3. CEO Briefing Integration
Weekly business audits automatically include:
- Total revenue from Odoo
- Outstanding invoices
- Payment trends
- Financial health metrics

---

## 🛠️ Management Scripts

### Initialize Database
```bash
./scripts/init_db.sh
```

### Backup Database
```bash
./scripts/backup.sh
# Creates backup in backups/ folder
```

### Restore Database
```bash
./scripts/restore.sh backups/backup_filename.sql
```

---

## 🔐 Security

### Production Deployment

For production use:

1. **Change default passwords:**
   - Update `admin_passwd` in `odoo.conf`
   - Update `POSTGRES_PASSWORD` in `docker-compose.yml`
   - Update database user password

2. **Enable HTTPS:**
   - Uncomment nginx service in `docker-compose.yml`
   - Add SSL certificates to `ssl/` folder
   - Configure `nginx.conf`

3. **Update odoo_config.json:**
   - Use strong passwords
   - Never commit credentials to git

### Security Checklist

- [ ] Changed admin password
- [ ] Changed database password
- [ ] Enabled HTTPS (production)
- [ ] Set up firewall rules
- [ ] Regular backups configured
- [ ] Odoo updated to latest version

---

## 📈 Monitoring

### Check Container Status
```bash
docker-compose ps
```

### View Logs
```bash
# All containers
docker-compose logs -f

# Odoo only
docker-compose logs -f odoo

# Database only
docker-compose logs -f odoo-db
```

### Health Check
```bash
# Check if Odoo is responding
curl http://localhost:8069

# Check database connection
docker exec odoo-db pg_isready -U odoo
```

---

## 🔄 Maintenance

### Update Odoo
```bash
docker-compose pull
docker-compose up -d
```

### Backup Data
```bash
# Backup database
docker exec odoo-db pg_dump -U odoo ai_employee > backups/backup_$(date +%Y%m%d).sql

# Backup file storage
docker cp odoo:/var/lib/odoo backups/odoo-files
```

### Restart Services
```bash
docker-compose restart
```

### Stop Odoo
```bash
docker-compose down
```

---

## 🆘 Troubleshooting

### Odoo Won't Start
```bash
# Check logs
docker-compose logs odoo

# Check if database is ready
docker-compose logs odoo-db

# Restart containers
docker-compose restart
```

### Port Already in Use
```bash
# Find process using port 8069
sudo lsof -i :8069

# Kill process or change port in docker-compose.yml
```

### Database Connection Failed
```bash
# Test database connection
docker exec odoo-db psql -U odoo -d postgres

# Reset database password
docker exec odoo-db psql -U odoo -c "ALTER USER odoo WITH PASSWORD 'odoo123';"
```

### Can't Access Odoo
```bash
# Check if container is running
docker-compose ps

# Check container IP
docker inspect odoo | grep IPAddress

# Try localhost:8069 in browser
```

---

## 📚 Resources

- **Odoo Documentation:** https://www.odoo.com/documentation/17.0/
- **Odoo Community GitHub:** https://github.com/odoo/odoo
- **MCP Server for Odoo:** https://github.com/AlanOgic/mcp-odoo-adv
- **AI Employee Skills:** ../Skills/OdooAccounting.md

---

## 🎯 Next Steps

After Odoo is running:

1. ✅ Complete initial setup (database, company, accounting)
2. ✅ Test AI Employee connection: `python odoo_accounting.py --test`
3. ✅ Create your first invoice in Odoo
4. ✅ Run financial summary: `python odoo_accounting.py --summary --days 30`
5. ✅ Generate CEO Briefing with Odoo data

---

**Odoo Status:** Ready to deploy with Docker Compose
**Last Updated:** 2026-04-11

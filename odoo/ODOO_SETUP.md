# Odoo Accounting Integration - Setup Guide

## Overview

Integrate Odoo Community Edition (free, open-source) with AI Employee for:
- Automatic invoice tracking
- Payment monitoring
- Financial reporting
- Bank reconciliation
- CEO Briefing revenue data

---

## Option 1: Local Installation (Recommended for Testing)

### Prerequisites

```bash
# Update system
sudo apt-get update

# Install dependencies
sudo apt-get install -y python3-pip python3-dev python3-venv \
    libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
    libjpeg-dev zlib1g-dev git wget
```

### Install PostgreSQL

```bash
# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-client

# Create Odoo user
sudo -u postgres createuser -s odoo

# Set password (remember this!)
sudo -u postgres psql -c "ALTER USER odoo WITH PASSWORD 'odoo123';"
```

### Install Odoo Community

```bash
# Create Odoo directory
sudo mkdir -p /opt/odoo
sudo chown $USER:$USER /opt/odoo

# Clone Odoo repository
cd /opt/odoo
git clone https://github.com/odoo/odoo.git --depth 1 --branch 17.0 odoo-server

# Create virtual environment
python3 -m venv odoo-venv
source odoo-venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r odoo-server/requirements.txt

# Create Odoo config directory
mkdir -p ~/.config/odoo
```

### Create Odoo Config File

```bash
cat > ~/.config/odoo/odoo.conf << 'EOF'
[options]
admin_passwd = admin123
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo123
db_host = localhost
addons_path = /opt/odoo/odoo-server/addons
data_dir = /opt/odoo/odoo-data
logfile = /opt/odoo/odoo.log
log_level = info
EOF
```

### Start Odoo

```bash
cd /opt/odoo
source odoo-venv/bin/activate
python3 odoo-server/odoo-bin -c ~/.config/odoo/odoo.conf
```

**Odoo will start on:** `http://localhost:8069`

---

## Option 2: Docker Installation (Easier)

### Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Run Odoo with Docker

```bash
# Create docker network
docker network create odoo-network

# Run PostgreSQL
docker run -d \
  --name odoo-db \
  --network odoo-network \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo123 \
  -e POSTGRES_DB=postgres \
  -v odoo-db-data:/var/lib/postgresql/data \
  postgres:15

# Run Odoo
docker run -d \
  --name odoo \
  --network odoo-network \
  -p 8069:8069 \
  -e HOST=odoo-db \
  -e PORT=5432 \
  -e USER=odoo \
  -e PASSWORD=odoo123 \
  -v odoo-data:/var/lib/odoo \
  odoo:17.0
```

**Access Odoo:** `http://localhost:8069`

---

## Option 3: Cloud VM (For Production)

### Deploy on Oracle Cloud Free Tier

```bash
# Create VM (Oracle Cloud Free Tier)
# Shape: VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM)
# Image: Ubuntu 22.04

# SSH into VM
ssh -i your_key.pem ubuntu@your-vm-ip

# Install Odoo (same as local installation)
# Follow Option 1 steps above
```

### Configure HTTPS (Production)

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create Nginx config
sudo cat > /etc/nginx/sites-available/odoo << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install SSL (Let's Encrypt)
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Odoo Initial Setup

### 1. Create Database

1. Open `http://localhost:8069`
2. Click "Create Database"
3. Enter:
   - **Master Password:** `admin123` (from config)
   - - **Database Name:** `ai_employee`
   - **Email:** your-email@example.com
   - **Password:** your-password

### 2. Install Accounting Module

1. Login to Odoo
2. Go to **Apps**
3. Search for "Accounting"
4. Click **Install** on "Invoicing" (free) or "Accounting" (full)

### 3. Configure Company

1. Go to **Settings** → **Companies**
2. Update:
   - Company Name
   - Currency
   - Fiscal Year
   - Chart of Accounts

### 4. Set Up Bank Accounts

1. Go to **Accounting** → **Configuration** → **Bank Accounts**
2. Click **Create**
3. Enter bank details:
   - Account Number
   - Bank Name
   - Account Type

---

## Odoo API Integration

### Get API Credentials

1. Go to **Settings** → **Users & Companies** → **Users**
2. Select your user
3. Enable **Technical Features**
4. Click **Action** → **Reset Password** (set API password)

### API Connection Details

```python
ODOO_CONFIG = {
    'url': 'http://localhost:8069',
    'db': 'ai_employee',
    'username': 'your-email@example.com',
    'password': 'your-password',
}
```

---

## Test Connection

```bash
# Test Odoo connection
python3 watchers/odoo_test_connection.py
```

---

## Next Steps

After Odoo is installed:
1. Run `watchers/odoo_mcp_server.py` (MCP integration)
2. Configure automatic bank sync
3. Set up invoice automation
4. Integrate with CEO Briefing

---

## Troubleshooting

### Odoo Won't Start
```bash
# Check logs
tail -f /opt/odoo/odoo.log

# Check PostgreSQL
sudo systemctl status postgresql
```

### Port Already in Use
```bash
# Find process using port 8069
sudo lsof -i :8069

# Kill process
sudo kill -9 <PID>
```

### Database Connection Failed
```bash
# Test PostgreSQL connection
psql -h localhost -U odoo -d postgres

# Reset password
sudo -u postgres psql -c "ALTER USER odoo WITH PASSWORD 'odoo123';"
```

---

## Resources

- **Odoo Documentation:** https://www.odoo.com/documentation
- **Odoo Community:** https://www.odoo.com/forum/help-1
- **GitHub:** https://github.com/odoo/odoo
- **MCP Server:** https://github.com/AlanOgic/mcp-odoo-adv

#!/bin/bash
# ══════════════════════════════════════════════════
#  Edcar Properties - Deployment Script
#  Run on a fresh Ubuntu 22.04 EC2 instance
#  bash deploy_edcar.sh
# ══════════════════════════════════════════════════

set -e
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo -e "${BLUE}   Edcar Properties - Production Deploy   ${NC}"
echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Please provide the following:${NC}"
echo ""
read -s -p "🔐 PostgreSQL password for DB user: " DB_PASSWORD
echo ""
read -p "📧 Mail username (Zoho email): " MAIL_USERNAME
read -s -p "🔑 Mail password (Zoho app password): " MAIL_PASSWORD
echo ""
read -p "📬 Admin email: " ADMIN_EMAIL
read -p "📱 Admin phone: " ADMIN_PHONE
read -p "🌐 Domain name (e.g. edcarproperties.co.zw or IP): " DOMAIN

echo ""
echo -e "${BLUE}▶ Setting up...${NC}"

# ── Generate secret key ───────────────────────────
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(64))")

# ── System packages ───────────────────────────────
echo -e "${YELLOW}▶ Installing packages...${NC}"
sudo apt update -qq
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib certbot python3-certbot-nginx -qq
echo -e "${GREEN}✅ Packages installed${NC}"

# ── PostgreSQL ────────────────────────────────────
echo -e "${YELLOW}▶ Setting up PostgreSQL...${NC}"
sudo systemctl start postgresql && sudo systemctl enable postgresql
sudo -u postgres psql <<EOF 2>/dev/null || true
CREATE DATABASE edcar_db;
CREATE USER edcar_user WITH PASSWORD '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE edcar_db TO edcar_user;
ALTER DATABASE edcar_db OWNER TO edcar_user;
EOF
echo -e "${GREEN}✅ PostgreSQL ready${NC}"

# ── Virtual environment ───────────────────────────
echo -e "${YELLOW}▶ Setting up Python environment...${NC}"
cd /home/ubuntu/edcar
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✅ Dependencies installed${NC}"

# ── Environment file ──────────────────────────────
echo -e "${YELLOW}▶ Writing environment variables...${NC}"
sudo tee /etc/edcar.env > /dev/null <<EOF
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=postgresql://edcar_user:${DB_PASSWORD}@localhost/edcar_db
MAIL_SERVER=smtp.zoho.com
MAIL_USERNAME=${MAIL_USERNAME}
MAIL_PASSWORD=${MAIL_PASSWORD}
ADMIN_EMAIL=${ADMIN_EMAIL}
ADMIN_PHONE=${ADMIN_PHONE}
PAYMENT_DETAILS=EcoCash: 0772 555 263 | CBZ Account: 0772 555 263 840 | Contact: +263 772 555 263
EOF
sudo chmod 644 /etc/edcar.env
echo -e "${GREEN}✅ Environment saved${NC}"

# ── Upload directories ────────────────────────────
echo -e "${YELLOW}▶ Creating upload directories...${NC}"
mkdir -p /home/ubuntu/edcar/app/static/uploads/{properties,proofs,projects,cars}
sudo chown -R ubuntu:www-data /home/ubuntu/edcar/app/static/uploads
sudo chmod -R 775 /home/ubuntu/edcar/app/static/uploads
sudo mkdir -p /var/log/edcar
echo -e "${GREEN}✅ Directories ready${NC}"

# ── Initialize database ───────────────────────────
echo -e "${YELLOW}▶ Initializing database...${NC}"
export FLASK_ENV=production
export DATABASE_URL="postgresql://edcar_user:${DB_PASSWORD}@localhost/edcar_db"
export SECRET_KEY="${SECRET_KEY}"
export MAIL_USERNAME="${MAIL_USERNAME}"
export MAIL_PASSWORD="${MAIL_PASSWORD}"
export ADMIN_EMAIL="${ADMIN_EMAIL}"
export ADMIN_PHONE="${ADMIN_PHONE}"
python3 -c "from app import create_app; app = create_app(); print('✅ Database initialized')"

# ── Nginx config ──────────────────────────────────
echo -e "${YELLOW}▶ Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/edcar > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    location /static/ {
        alias /home/ubuntu/edcar/app/static/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    client_max_body_size 32M;
}
EOF
sudo ln -sf /etc/nginx/sites-available/edcar /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
echo -e "${GREEN}✅ Nginx configured (port 8001)${NC}"

# ── Systemd service ───────────────────────────────
echo -e "${YELLOW}▶ Creating systemd service...${NC}"
sudo tee /etc/systemd/system/edcar.service > /dev/null <<EOF
[Unit]
Description=Gunicorn for Edcar Properties
After=network.target postgresql.service

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/edcar
EnvironmentFile=/etc/edcar.env
ExecStart=/home/ubuntu/edcar/venv/bin/gunicorn \\
    --workers 3 \\
    --bind 127.0.0.1:8001 \\
    --timeout 120 \\
    --access-logfile /var/log/edcar/access.log \\
    --error-logfile /var/log/edcar/error.log \\
    wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable edcar
sudo systemctl start edcar
sleep 3
echo -e "${GREEN}✅ Service started${NC}"

# ── Final status ──────────────────────────────────
STATUS=$(sudo systemctl is-active edcar)
if [ "$STATUS" = "active" ]; then
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ Edcar Properties is LIVE!            ${NC}"
    echo -e "${GREEN}══════════════════════════════════════════${NC}"
    echo ""
    echo -e "  🌐 Website:  ${BLUE}http://${DOMAIN}${NC}"
    echo -e "  👤 Admin:    ${BLUE}http://${DOMAIN}/admin/dashboard${NC}"
    echo -e "  📧 Login:    admin@edcarproperties.co.zw"
    echo -e "  🔑 Password: admin1234"
    echo ""
    echo -e "  ${YELLOW}⚠️  Change the admin password after first login!${NC}"
    echo ""
    echo -e "  Commands:"
    echo -e "  ${BLUE}sudo systemctl restart edcar${NC}   — Restart"
    echo -e "  ${BLUE}sudo journalctl -u edcar -f${NC}    — Logs"
    echo ""
    echo -e "  📝 Note: Edcar runs on port 8001"
    echo -e "  (jobboard.co.zw still runs on port 8000)"
    echo ""
else
    echo -e "${RED}❌ Service failed to start${NC}"
    echo "  sudo journalctl -u edcar -f"
fi

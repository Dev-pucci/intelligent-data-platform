# Deployment Options: VPS vs Local with nginx

## Understanding the Difference

### What nginx Does

**nginx** is a web server and reverse proxy that:
- Routes incoming HTTP/HTTPS requests to your applications
- Handles SSL/TLS certificates (HTTPS)
- Load balances across multiple servers
- Serves static files efficiently
- Compresses responses
- Caches content

**nginx CANNOT replace a VPS** - it's software that runs ON a server (local or VPS).

---

## Deployment Scenarios

### Option 1: Local Development (Current Setup)
**What you have now**:
- n8n running on `http://localhost:5678`
- PostgreSQL on `localhost:5432`
- Only accessible from your computer
- No nginx needed

**Good for**:
✓ Development
✓ Testing
✓ Learning
✓ Personal use on one computer

**Limitations**:
✗ Not accessible from internet
✗ Not accessible from other devices
✗ No HTTPS
✗ Single computer only

---

### Option 2: Local Network with nginx
**What this adds**:
- nginx reverse proxy on your computer
- n8n accessible from other devices on your network
- Professional URLs like `http://scraper.local`
- Still not accessible from internet

**Setup Required**:
1. Install nginx on Windows
2. Configure reverse proxy
3. Update hosts file on other devices

**Good for**:
✓ Multiple computers on same network
✓ Team working from same office/home
✓ Professional local setup
✓ Testing before VPS deployment

**Limitations**:
✗ Still not accessible from internet
✗ No HTTPS (without additional setup)
✗ Limited to local network

---

### Option 3: VPS Deployment with nginx (Production)
**What this provides**:
- Server running 24/7 in a datacenter
- Accessible from anywhere via internet
- nginx as reverse proxy
- HTTPS with SSL certificates
- Professional domain (e.g., scraper.yourdomain.com)

**Setup Required**:
1. Rent VPS (DigitalOcean, Linode, AWS, etc.)
2. Install Ubuntu/Debian Linux
3. Install PostgreSQL, Node.js, nginx
4. Deploy your platform
5. Configure domain and SSL

**Good for**:
✓ Production use
✓ Remote access
✓ Team collaboration from anywhere
✓ 24/7 availability
✓ Professional deployment

**Cost**:
- VPS: $5-20/month
- Domain: $10-15/year
- SSL: Free (Let's Encrypt)

---

## Recommended: Local nginx Setup (No VPS Needed)

For your use case, you can use nginx locally to:
1. Access n8n on a clean URL (`http://scraper.local` instead of `localhost:5678`)
2. Add HTTPS support locally
3. Prepare for future VPS deployment
4. Professional development environment

### Architecture

```
Browser Request
    ↓
nginx (Port 80/443)
    ↓
Reverse Proxy
    ↓
n8n (Port 5678)
    ↓
PostgreSQL (Port 5432)
```

---

## nginx Setup for Windows (Local)

### Step 1: Install nginx

**Download**:
- Go to: http://nginx.org/en/download.html
- Download: nginx/Windows (stable version)
- Extract to: `C:\nginx`

**Or via Chocolatey**:
```bash
choco install nginx
```

### Step 2: Create nginx Configuration

**File**: `C:\nginx\conf\nginx.conf`

```nginx
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    # n8n Workflow Automation
    upstream n8n {
        server 127.0.0.1:5678;
    }

    # PostgreSQL Admin (pgAdmin - optional)
    upstream pgadmin {
        server 127.0.0.1:5050;
    }

    # Main Server Block
    server {
        listen       80;
        server_name  scraper.local;

        # n8n workflows
        location / {
            proxy_pass http://n8n;
            proxy_http_version 1.1;

            # WebSocket support (required for n8n)
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Headers
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    # pgAdmin (optional database management)
    server {
        listen       80;
        server_name  pgadmin.local;

        location / {
            proxy_pass http://pgadmin;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### Step 3: Update Windows Hosts File

**File**: `C:\Windows\System32\drivers\etc\hosts`

Add these lines:
```
127.0.0.1   scraper.local
127.0.0.1   pgadmin.local
```

**Note**: You need Administrator privileges to edit this file.

### Step 4: Start nginx

**Command Prompt (as Administrator)**:
```bash
cd C:\nginx
start nginx
```

**Verify it's running**:
```bash
curl http://scraper.local
```

### Step 5: Test Access

Open browser:
- **n8n**: http://scraper.local
- **pgAdmin**: http://pgadmin.local (if installed)

---

## nginx Management Commands (Windows)

### Start nginx
```bash
cd C:\nginx
start nginx
```

### Stop nginx
```bash
cd C:\nginx
nginx -s stop
```

### Reload Configuration
```bash
cd C:\nginx
nginx -s reload
```

### Test Configuration
```bash
cd C:\nginx
nginx -t
```

### Check nginx Status
```bash
tasklist /fi "imagename eq nginx.exe"
```

---

## Adding HTTPS (Local Development)

### Generate Self-Signed Certificate

**Using OpenSSL**:
```bash
# Install OpenSSL first (via Chocolatey)
choco install openssl

# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout C:\nginx\conf\ssl\scraper.local.key \
  -out C:\nginx\conf\ssl\scraper.local.crt \
  -subj "/CN=scraper.local"
```

### Update nginx Configuration

```nginx
server {
    listen       443 ssl;
    server_name  scraper.local;

    ssl_certificate      C:/nginx/conf/ssl/scraper.local.crt;
    ssl_certificate_key  C:/nginx/conf/ssl/scraper.local.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://n8n;
        # ... (same proxy settings as before)
    }
}

# Redirect HTTP to HTTPS
server {
    listen       80;
    server_name  scraper.local;
    return 301 https://$server_name$request_uri;
}
```

**Access**: https://scraper.local

**Note**: Browser will show security warning (normal for self-signed certificates).

---

## VPS Deployment Guide (When Ready)

### Prerequisites
- Domain name (e.g., yourdomain.com)
- VPS account (DigitalOcean, Linode, AWS)
- SSH access

### VPS Providers (Recommended)

| Provider | Starting Price | RAM | Storage |
|----------|---------------|-----|---------|
| **DigitalOcean** | $6/month | 1GB | 25GB SSD |
| **Linode** | $5/month | 1GB | 25GB SSD |
| **Vultr** | $5/month | 1GB | 25GB SSD |
| **Hetzner** | $4/month | 2GB | 20GB SSD |
| **AWS Lightsail** | $5/month | 1GB | 40GB SSD |

### Deployment Steps

#### 1. Create VPS
```bash
# Choose Ubuntu 22.04 LTS
# Add your SSH key
# Select datacenter near you
```

#### 2. Connect to VPS
```bash
ssh root@your-vps-ip
```

#### 3. Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install PostgreSQL
apt install -y postgresql postgresql-contrib

# Install nginx
apt install -y nginx

# Install certbot (for SSL)
apt install -y certbot python3-certbot-nginx

# Install Git
apt install -y git
```

#### 4. Configure PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE scraper_db;
CREATE USER scraper_user WITH PASSWORD 'strong-password-here';
GRANT ALL PRIVILEGES ON DATABASE scraper_db TO scraper_user;
\q
```

#### 5. Deploy Application
```bash
# Create app user
useradd -m -s /bin/bash scraper
su - scraper

# Clone repository (or upload files)
git clone https://github.com/yourusername/intelligent-data-platform.git
cd intelligent-data-platform

# Install n8n
npm install n8n

# Create .env file
nano .env
# Add production configuration
```

#### 6. Configure nginx
```bash
# Create nginx config
nano /etc/nginx/sites-available/scraper

# Add configuration (see below)

# Enable site
ln -s /etc/nginx/sites-available/scraper /etc/nginx/sites-enabled/

# Test config
nginx -t

# Reload nginx
systemctl reload nginx
```

**nginx VPS Configuration**:
```nginx
server {
    server_name scraper.yourdomain.com;

    location / {
        proxy_pass http://localhost:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 7. Get SSL Certificate
```bash
certbot --nginx -d scraper.yourdomain.com
```

#### 8. Create Systemd Service
```bash
nano /etc/systemd/system/n8n.service
```

```ini
[Unit]
Description=n8n Workflow Automation
After=network.target

[Service]
Type=simple
User=scraper
WorkingDirectory=/home/scraper/intelligent-data-platform
Environment="N8N_PORT=5678"
Environment="N8N_PROTOCOL=https"
Environment="N8N_HOST=scraper.yourdomain.com"
Environment="WEBHOOK_URL=https://scraper.yourdomain.com/"
ExecStart=/usr/bin/npx n8n start
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
systemctl enable n8n
systemctl start n8n
systemctl status n8n
```

#### 9. Configure Domain DNS

Point your domain to VPS IP:
```
Type: A
Name: scraper
Value: your-vps-ip
TTL: 3600
```

#### 10. Access Your Deployment

**URL**: https://scraper.yourdomain.com

---

## Comparison Table

| Feature | Local (No nginx) | Local + nginx | VPS + nginx |
|---------|-----------------|---------------|-------------|
| **Cost** | Free | Free | $5-20/month |
| **Access** | This computer only | Local network | Anywhere (internet) |
| **URL** | localhost:5678 | scraper.local | scraper.yourdomain.com |
| **HTTPS** | No | Yes (self-signed) | Yes (Let's Encrypt) |
| **24/7 Availability** | No | No | Yes |
| **Team Access** | No | Local network only | Yes |
| **Professional** | Development | Development/Testing | Production |
| **Setup Difficulty** | Easy | Medium | Advanced |
| **Maintenance** | None | Low | Medium |

---

## Recommendation

### For You Right Now

**Start with Local nginx** (Option 2):
- Professional local setup
- Clean URLs
- Practice for production
- No cost
- Easy to remove if not needed

**Benefits**:
1. Access n8n at `http://scraper.local` instead of `localhost:5678`
2. Professional development environment
3. Prepare configuration for future VPS
4. Learn nginx before production
5. Impress yourself! 😊

### When to Move to VPS

Move to VPS (Option 3) when you need:
- Remote access (work from anywhere)
- Team collaboration
- 24/7 availability
- Production deployment
- Client/customer access
- Professional domain

---

## Quick Start: Local nginx Setup

### 1. Install nginx
```bash
choco install nginx
```

### 2. Copy Configuration
Save the nginx.conf from above to `C:\nginx\conf\nginx.conf`

### 3. Update Hosts File
Add `127.0.0.1 scraper.local` to `C:\Windows\System32\drivers\etc\hosts`

### 4. Start nginx
```bash
cd C:\nginx
start nginx
```

### 5. Access n8n
Open browser: http://scraper.local

**Done!** 🎉

---

## Summary

**Question**: Can nginx replace VPS?
**Answer**: No - nginx is software, VPS is a server

**Better Question**: Do you need a VPS?
**Answer**: Not yet! Use local nginx first

**Local nginx gives you**:
- ✓ Professional setup
- ✓ Clean URLs
- ✓ Practice for production
- ✓ Zero cost
- ✓ Easy to set up

**When you need VPS**:
- Remote access required
- Team collaboration
- 24/7 availability
- Production deployment

---

**Next Step**: Want me to create the nginx configuration files and setup scripts for local deployment?

# nginx Quick Start Guide

## TL;DR - Your Question Answered

**Q: Can nginx replace VPS deployment?**

**A: NO** - nginx is software, VPS is hardware/server

### What They Are:
- **nginx** = Web server software (traffic router)
- **VPS** = Virtual Private Server (the actual computer)

### What You Need:
- **For local dev**: nginx on your computer ✓ (No VPS needed)
- **For production**: nginx on VPS ✓ (Both needed)

---

## Quick Setup (5 Minutes)

### Prerequisites
- Windows 10/11
- Administrator access
- n8n already running

### Steps

#### 1. Run Setup Script (as Administrator)
```batch
Right-click: nginx\setup-nginx-windows.bat
Select: "Run as administrator"
```

#### 2. Start nginx
```batch
cd C:\nginx
start nginx
```

#### 3. Access n8n
Open browser: **http://scraper.local**

**Done!** ✓

---

## What This Gives You

### Before (No nginx)
- URL: `http://localhost:5678`
- Access: This computer only
- URLs: Technical, not professional

### After (With nginx)
- URL: `http://scraper.local`
- Access: All devices on your network (optional)
- URLs: Clean, professional
- Ready for production deployment later

---

## Manual Setup (If Script Fails)

### Step 1: Install nginx

**Option A: Chocolatey (Recommended)**
```batch
choco install nginx
```

**Option B: Manual Download**
1. Go to: http://nginx.org/en/download.html
2. Download: nginx/Windows (stable)
3. Extract to: `C:\nginx`

### Step 2: Copy Configuration

Copy `nginx/nginx.conf` to `C:\nginx\conf\nginx.conf`

### Step 3: Update Hosts File

Edit: `C:\Windows\System32\drivers\etc\hosts`

Add these lines:
```
127.0.0.1   scraper.local
127.0.0.1   api.scraper.local
127.0.0.1   grafana.scraper.local
```

**Note**: Requires Administrator privileges

### Step 4: Test Configuration

```batch
cd C:\nginx
nginx -t
```

Should show: "test is successful"

### Step 5: Start nginx

```batch
cd C:\nginx
start nginx
```

### Step 6: Verify

```batch
curl http://scraper.local/health
```

Should return: "n8n proxy healthy"

---

## nginx Management

### Start nginx
```batch
cd C:\nginx
start nginx
```

### Stop nginx
```batch
cd C:\nginx
nginx -s stop
```

### Reload Configuration
```batch
cd C:\nginx
nginx -s reload
```

### Test Configuration
```batch
cd C:\nginx
nginx -t
```

### Check if Running
```batch
tasklist /fi "imagename eq nginx.exe"
```

---

## Accessing Services

With nginx running:

| Service | Old URL | New URL |
|---------|---------|---------|
| **n8n** | http://localhost:5678 | http://scraper.local |
| **API** (future) | http://localhost:8000 | http://api.scraper.local |
| **Grafana** (future) | http://localhost:3000 | http://grafana.scraper.local |

---

## Troubleshooting

### nginx won't start

**Error**: "bind() to 0.0.0.0:80 failed"

**Solution**: Another service is using port 80
```batch
# Find what's using port 80
netstat -ano | findstr :80

# Stop IIS if running
iisreset /stop
```

### Can't access scraper.local

**Check 1**: Is nginx running?
```batch
tasklist /fi "imagename eq nginx.exe"
```

**Check 2**: Is hosts file updated?
```batch
type C:\Windows\System32\drivers\etc\hosts | findstr scraper
```

**Check 3**: Is n8n running?
```batch
curl http://localhost:5678
```

### Page shows 502 Bad Gateway

**Cause**: n8n is not running

**Solution**: Start n8n
```batch
cd C:\Users\PUCCI\Desktop\gem\intelligent-data-platform
npx n8n start
```

---

## Benefits of This Setup

### For Development
✓ Professional URLs
✓ Practice production setup
✓ Easy to remember addresses
✓ Prepare for VPS deployment

### For Future Production
✓ Same nginx config works on VPS
✓ Easy migration path
✓ Already understand the setup
✓ Just add domain and SSL

---

## Next Steps

### Now (With Local nginx)
1. Access n8n at `http://scraper.local`
2. Import workflows
3. Configure PostgreSQL
4. Build automation

### Later (Production Deployment)
1. Rent VPS ($5-20/month)
2. Point domain to VPS
3. Copy nginx config to VPS
4. Add SSL certificate (free)
5. Access from anywhere!

See [DEPLOYMENT_OPTIONS.md](../DEPLOYMENT_OPTIONS.md) for VPS guide.

---

## Summary

**You asked**: Can nginx replace VPS?

**Answer**:
- nginx = Software ❌ Not a server
- VPS = Server ✓ Where software runs

**What you can do NOW**:
- Use nginx locally ✓ (No VPS needed)
- Professional development setup ✓
- Free ✓
- Ready for future VPS ✓

**When you need VPS**:
- Remote access required
- 24/7 availability
- Team collaboration
- Production deployment

---

## Files in This Directory

- `nginx.conf` - Main configuration file
- `setup-nginx-windows.bat` - Automated setup script
- `NGINX_QUICK_START.md` - This file
- `README.md` - Directory overview

---

**Quick Start Command**:
```batch
# Run as Administrator
nginx\setup-nginx-windows.bat

# Then access
http://scraper.local
```

**That's it!** 🚀

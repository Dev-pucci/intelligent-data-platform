# Quick Start Guide

## n8n Workflow Automation

### ✓ Status: Running

**Access n8n**: http://localhost:5678

---

## Quick Commands

### Start n8n
```bash
.\start-n8n.bat        # Windows
./start-n8n.sh         # Linux/Mac
npx n8n start          # Direct command
```

### Stop n8n
Press `Ctrl+C` in the running terminal

### Check Status
```bash
curl http://localhost:5678
```

---

## Database Connection (PostgreSQL)

Use these settings in n8n PostgreSQL nodes:

```
Host: localhost
Port: 5432
Database: scraper_db
User: scraper_user
Password: 123456
```

---

## Integration Points

### 1. Run Python Scraper
**Node**: Execute Command
```bash
cd /path/to/intelligent-data-platform
python -m scrapers.scraper_runner --config configs/sites/jumia_spa.yml
```

### 2. Fetch URLs from Database
**Node**: PostgreSQL
```sql
SELECT id, url, config_name
FROM scraping_queue
WHERE status = 'pending'
LIMIT 10;
```

### 3. Store Scraped Data
**Node**: PostgreSQL
```sql
INSERT INTO scraped_data (source_url, raw_data, data_hash, created_at)
VALUES ($1, $2, $3, NOW());
```

---

## File Locations

- **Web UI**: http://localhost:5678
- **Config**: [.env](.env)
- **Workflows**: `n8n-workflows/`
- **Docs**: [N8N_SETUP_GUIDE.md](N8N_SETUP_GUIDE.md)
- **Complete Guide**: [N8N_INSTALLATION_COMPLETE.md](N8N_INSTALLATION_COMPLETE.md)

---

## Next Steps

1. Open http://localhost:5678
2. Create your first workflow
3. Add PostgreSQL node
4. Connect to scraper_db
5. Build scraping automation

---

*For detailed information, see [N8N_INSTALLATION_COMPLETE.md](N8N_INSTALLATION_COMPLETE.md)*

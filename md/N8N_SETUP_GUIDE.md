# n8n Workflow Automation Setup Guide

## Overview

n8n is an open-source workflow automation tool that will orchestrate the Intelligent Data Acquisition Platform's scraping, parsing, and data processing workflows.

---

## Installation Status

**Status**: Installing n8n v1.116.2
**Method**: Local npm installation
**Installation Command**: `npm install n8n --save`

The installation is currently in progress. n8n is a large package (~400MB) with many dependencies, so installation may take 10-15 minutes.

---

## Configuration

### Environment Variables

All n8n configuration is stored in [.env](.env):

```env
# n8n Configuration
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_GENERIC_TIMEZONE=Africa/Nairobi
N8N_EDITOR_BASE_URL=http://localhost:5678
N8N_WEBHOOK_BASE_URL=http://localhost:5678
N8N_ENCRYPTION_KEY=n8n-encryption-key-change-this
N8N_USER_MANAGEMENT_DISABLED=true
N8N_BASIC_AUTH_ACTIVE=false
N8N_METRICS=true
```

### Key Settings Explained

| Setting | Value | Purpose |
|---------|-------|---------|
| `N8N_PORT` | 5678 | Web interface port |
| `N8N_GENERIC_TIMEZONE` | Africa/Nairobi | Timezone for scheduled workflows |
| `N8N_USER_MANAGEMENT_DISABLED` | true | Disable user management for local development |
| `N8N_BASIC_AUTH_ACTIVE` | false | No authentication for local access |
| `N8N_METRICS` | true | Enable Prometheus metrics |

---

## Starting n8n

### Option 1: Windows Batch Script

```batch
.\start-n8n.bat
```

### Option 2: Linux/Mac Shell Script

```bash
./start-n8n.sh
```

### Option 3: Direct Command

```bash
npx n8n start
```

### Option 4: With Environment File

```bash
export $(cat .env | grep -v '^#' | xargs)
npx n8n start
```

---

## Accessing n8n

Once n8n is running:

1. **Web Interface**: http://localhost:5678
2. **API Endpoint**: http://localhost:5678/api/v1
3. **Webhook Endpoint**: http://localhost:5678/webhook

---

## Project Integration

### Directory Structure

```
intelligent-data-platform/
├── n8n-workflows/          # Store exported n8n workflows here
│   ├── scraping-pipeline.json
│   ├── data-validation.json
│   └── monitoring-alerts.json
├── start-n8n.bat           # Windows startup script
├── start-n8n.sh            # Linux/Mac startup script
└── .env                    # n8n configuration
```

### Workflow Storage

- **Location**: `n8n-workflows/` directory
- **Format**: JSON files
- **Version Control**: Commit workflows to Git
- **Import/Export**: Use n8n UI or CLI

---

## Planned Workflows

### 1. **Scraping Pipeline** (`scraping-pipeline.json`)
```
[Trigger: Schedule]
    ↓
[HTTP Request: Fetch URLs from database]
    ↓
[Execute: Run scraper with config]
    ↓
[Parser: Extract structured data]
    ↓
[Database: Store in PostgreSQL]
    ↓
[Notification: Send success/error alert]
```

### 2. **Data Validation** (`data-validation.json`)
```
[Trigger: Webhook from scraper]
    ↓
[Validator: Check data quality]
    ↓
[Switch: Valid/Invalid]
    ├─ Valid → Store in database
    └─ Invalid → Log error + Alert
```

### 3. **Monitoring & Alerts** (`monitoring-alerts.json`)
```
[Trigger: Every 5 minutes]
    ↓
[HTTP: Check scraper health]
    ↓
[HTTP: Check database connection]
    ↓
[HTTP: Check Redis connection]
    ↓
[Switch: All healthy?]
    ├─ Yes → Update metrics
    └─ No → Send alert
```

### 4. **Multi-Level Scraping** (`multi-level-scraping.json`)
```
[Trigger: Manual/Schedule]
    ↓
[Execute: Scrape listing pages]
    ↓
[Loop: For each product URL]
    │   ↓
    │   [Wait: Rate limiting delay]
    │   ↓
    │   [Execute: Scrape detail page]
    │   ↓
    │   [Merge: Combine listing + detail data]
    ↓
[Database: Bulk insert all products]
```

---

## n8n Nodes for This Project

### Built-in Nodes to Use

| Node Type | Use Case |
|-----------|----------|
| **HTTP Request** | Call scraper API, fetch URLs |
| **Execute Command** | Run Python scrapers directly |
| **PostgreSQL** | Read/write to database |
| **Redis** | Cache management, queue handling |
| **Code** | Custom JavaScript/Python logic |
| **Schedule Trigger** | Run scrapers at intervals |
| **Webhook** | Receive scraper notifications |
| **Switch** | Route data based on conditions |
| **Loop Over Items** | Process multiple URLs |
| **Set** | Transform data structure |
| **Wait** | Rate limiting delays |
| **Error Trigger** | Handle failures |
| **Slack/Email** | Send alerts |

### Custom Nodes (Future Enhancement)

- **Scraper Node**: Direct integration with Python scrapers
- **Parser Node**: Call parser_manager directly
- **Crawler Node**: Trigger crawler_engine
- **Config Loader**: Load .yml configs dynamically

---

## Database Integration

### PostgreSQL Node Configuration

```json
{
  "host": "localhost",
  "port": 5432,
  "database": "scraper_db",
  "user": "scraper_user",
  "password": "123456",
  "ssl": false
}
```

### Example Query Nodes

**1. Fetch Pending URLs**
```sql
SELECT id, url, config_name
FROM scraping_queue
WHERE status = 'pending'
LIMIT 10;
```

**2. Insert Scraped Data**
```sql
INSERT INTO scraped_data (source_url, raw_data, data_hash, created_at)
VALUES ($1, $2, $3, NOW());
```

**3. Update Job Status**
```sql
UPDATE scraping_jobs
SET status = 'completed',
    items_scraped = $1,
    completed_at = NOW()
WHERE id = $2;
```

---

## API Integration

### Calling Python Scrapers

#### Execute Command Node
```bash
cd /path/to/intelligent-data-platform
python -m scrapers.scraper_runner \
    --config configs/sites/jumia_spa.yml \
    --output /tmp/output.json
```

#### HTTP Request Node (Future)
```
POST http://localhost:8000/api/v1/scrape
{
  "config": "jumia_spa",
  "urls": ["https://jumia.co.ke/phones/"],
  "parser_type": "css"
}
```

---

## Monitoring Integration

### Prometheus Metrics

When `N8N_METRICS=true`, n8n exposes metrics at:
```
http://localhost:5678/metrics
```

### Grafana Integration

1. Add n8n as Prometheus data source
2. Import n8n dashboard
3. Monitor:
   - Workflow execution count
   - Workflow success/failure rate
   - Execution duration
   - Active workflows

---

## Best Practices

### 1. **Error Handling**
- Add Error Trigger nodes to every workflow
- Log errors to database
- Send alerts for critical failures
- Implement retry logic with exponential backoff

### 2. **Rate Limiting**
- Use Wait nodes between scraper calls
- Respect website rate limits (from configs)
- Implement queue-based processing
- Monitor API quotas

### 3. **Data Validation**
- Validate scraped data before storage
- Check for required fields
- Verify data types
- Detect duplicate records

### 4. **Workflow Organization**
- Use descriptive workflow names
- Add notes/documentation in workflows
- Group related nodes
- Use color coding for node types
- Version control workflows in Git

### 5. **Performance**
- Use batch processing where possible
- Implement caching (Redis)
- Limit concurrent executions
- Monitor memory usage
- Clean up old execution data

---

## Troubleshooting

### n8n Won't Start

**Check Node.js version**:
```bash
node --version  # Should be v18+ or v20+
```

**Check port availability**:
```bash
netstat -ano | findstr :5678  # Windows
lsof -i :5678                 # Linux/Mac
```

**Check environment variables**:
```bash
cat .env | grep N8N
```

### Workflows Not Executing

1. Check trigger configuration (schedule, webhook URL)
2. Verify workflow is activated (toggle switch)
3. Check execution logs in n8n UI
4. Verify database/API connections
5. Check node credentials

### Database Connection Errors

1. Verify PostgreSQL is running
2. Check credentials in .env
3. Test connection manually:
   ```bash
   psql -U scraper_user -d scraper_db -h localhost
   ```
4. Check firewall rules

---

## Security Recommendations

### For Production Deployment

```env
# Enable user management
N8N_USER_MANAGEMENT_DISABLED=false

# Enable basic auth
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=<strong-password>

# Or use JWT
N8N_JWT_AUTH_ACTIVE=true
N8N_JWT_AUTH_HEADER=Authorization

# Change encryption key
N8N_ENCRYPTION_KEY=<generate-random-32-char-key>

# Use HTTPS
N8N_PROTOCOL=https
N8N_SSL_KEY=/path/to/key.pem
N8N_SSL_CERT=/path/to/cert.pem
```

### Database Credentials

- Store PostgreSQL password in environment variable
- Use `.pgpass` file for automatic authentication
- Implement connection pooling
- Use read-only credentials where possible

---

## Next Steps

1. ✓ Install n8n (in progress)
2. ✓ Configure environment variables
3. ✓ Create startup scripts
4. ⏳ Start n8n server
5. ⏳ Access web interface
6. ⏳ Create first workflow
7. ⏳ Connect to PostgreSQL
8. ⏳ Test scraping pipeline
9. ⏳ Set up monitoring
10. ⏳ Deploy to production

---

## Resources

- **Official Docs**: https://docs.n8n.io/
- **Community Forum**: https://community.n8n.io/
- **GitHub**: https://github.com/n8n-io/n8n
- **Workflow Templates**: https://n8n.io/workflows/
- **API Documentation**: https://docs.n8n.io/api/

---

**Generated**: 2025-10-26
**Platform**: Intelligent Data Acquisition Platform
**Version**: n8n v1.116.2

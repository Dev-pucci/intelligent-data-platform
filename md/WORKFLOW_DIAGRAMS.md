# n8n Workflow Diagrams

## Visual Guide to Created Workflows

---

## Workflow 1: Manual Test Scraper

**Purpose**: Quick testing of the scraping pipeline with manual execution

```
┌─────────────────┐
│ Manual Trigger  │  ← Click to run
│  (You click)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Run Test Pipeline                  │
│  Execute Command Node               │
│  ─────────────────────────────      │
│  cd "...\intelligent-data-platform" │
│  python test_full_pipeline.py       │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Fetch Latest Data                  │
│  PostgreSQL Node                    │
│  ─────────────────────────────      │
│  SELECT * FROM scraped_data         │
│  ORDER BY created_at DESC           │
│  LIMIT 10;                          │
└─────────────────────────────────────┘
         │
         ▼
    [Results]
```

**Usage**:
1. Open workflow in n8n
2. Click "Execute Workflow"
3. View results in each node

---

## Workflow 2: Scheduled Scraping Pipeline

**Purpose**: Automated daily scraping with error handling and notifications

```
┌──────────────────────┐
│  Schedule Trigger    │  ← Runs daily at 2 AM
│  Cron: 0 2 * * *     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Execute Scraper                     │
│  Execute Command Node                │
│  ──────────────────────────────      │
│  cd "...\intelligent-data-platform"  │
│  python test_full_pipeline.py        │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Parse Results                       │
│  Function Node                       │
│  ──────────────────────────────      │
│  Extract:                            │
│  - Success/failure status            │
│  - Items scraped count               │
│  - Items inserted count              │
│  - Error messages                    │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Verify Database                     │
│  PostgreSQL Node                     │
│  ──────────────────────────────      │
│  SELECT COUNT(*) as total_records,   │
│         MAX(created_at) as latest,   │
│         COUNT(DISTINCT source_url)   │
│  FROM scraped_data                   │
│  WHERE created_at >= NOW() - '1h'    │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Check Success                       │
│  IF Node                             │
│  ──────────────────────────────      │
│  Condition: status == 'completed'    │
└──────────┬───────────────────────────┘
           │
           ├─── TRUE ───┐
           │            │
           │            ▼
           │   ┌────────────────────────────────┐
           │   │  Success Notification          │
           │   │  Function Node                 │
           │   │  ────────────────────────────  │
           │   │  Build notification:           │
           │   │  - Title: "Job Completed"      │
           │   │  - Items scraped               │
           │   │  - Database stats              │
           │   └────────────────────────────────┘
           │
           └─── FALSE ───┐
                        │
                        ▼
               ┌────────────────────────────────┐
               │  Error Notification            │
               │  Function Node                 │
               │  ────────────────────────────  │
               │  Build notification:           │
               │  - Title: "Job Failed"         │
               │  - Error details               │
               │  - Debug information           │
               └────────────────────────────────┘
```

**Features**:
- ✓ Automated daily execution
- ✓ Result parsing
- ✓ Database verification
- ✓ Success/failure routing
- ✓ Detailed notifications

---

## Future Workflow: Multi-Level Scraping

**Purpose**: Scrape listing pages, then detail pages for each item

```
┌──────────────────────┐
│  Schedule Trigger    │
│  or Manual Trigger   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Fetch Pending URLs                  │
│  PostgreSQL Node                     │
│  ──────────────────────────────      │
│  SELECT * FROM scraping_queue        │
│  WHERE status = 'pending'            │
│  LIMIT 10                            │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Loop Over URLs                      │
│  Loop Node                           │
│  ──────────────────────────────      │
│  For each URL in queue               │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Scrape Listing Page                 │
│  Execute Command Node                │
│  ──────────────────────────────      │
│  python -m scrapers.scraper_runner   │
│  --config {{$json.config_name}}      │
│  --url {{$json.url}}                 │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Parse Listing Results               │
│  Function Node                       │
│  ──────────────────────────────      │
│  Extract product URLs from listing   │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Loop Over Product URLs              │
│  Loop Node                           │
│  ──────────────────────────────      │
│  For each product URL                │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Wait (Rate Limiting)                │
│  Wait Node                           │
│  ──────────────────────────────      │
│  Delay: 2 seconds                    │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Scrape Detail Page                  │
│  Execute Command Node                │
│  ──────────────────────────────      │
│  Scrape individual product details   │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Merge Listing + Detail Data         │
│  Function Node                       │
│  ──────────────────────────────      │
│  Combine data from both levels       │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Insert into Database                │
│  PostgreSQL Node                     │
│  ──────────────────────────────      │
│  INSERT INTO scraped_data ...        │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Update Job Status                   │
│  PostgreSQL Node                     │
│  ──────────────────────────────      │
│  UPDATE scraping_queue               │
│  SET status = 'completed'            │
└──────────────────────────────────────┘
```

---

## Future Workflow: Health Monitoring

**Purpose**: Monitor system health and send alerts

```
┌──────────────────────┐
│  Schedule Trigger    │  ← Every 5 minutes
│  Cron: */5 * * * *   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Check PostgreSQL Health             │
│  PostgreSQL Node                     │
│  ──────────────────────────────      │
│  SELECT 1 as health_check            │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Check Database Size                 │
│  PostgreSQL Node                     │
│  ──────────────────────────────      │
│  SELECT pg_database_size('scraper')  │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Check Recent Scrapes                │
│  PostgreSQL Node                     │
│  ──────────────────────────────      │
│  SELECT COUNT(*) FROM scraped_data   │
│  WHERE created_at >= NOW() - '1h'    │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Aggregate Health Status             │
│  Function Node                       │
│  ──────────────────────────────      │
│  Combine all health checks           │
│  Calculate overall status            │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Check If All Healthy                │
│  IF Node                             │
│  ──────────────────────────────      │
│  Condition: all_checks_passed        │
└──────────┬───────────────────────────┘
           │
           ├─── TRUE ───┐
           │            │
           │            ▼
           │   ┌────────────────────────┐
           │   │  Update Metrics        │
           │   │  (Future: Prometheus)  │
           │   └────────────────────────┘
           │
           └─── FALSE ───┐
                        │
                        ▼
               ┌────────────────────────┐
               │  Send Alert            │
               │  (Future: Email/Slack) │
               └────────────────────────┘
```

---

## Node Types Reference

### Available in Created Workflows

| Node Type | Purpose | Configuration |
|-----------|---------|---------------|
| **Manual Trigger** | Start workflow manually | No config needed |
| **Schedule Trigger** | Run on schedule | Cron expression: `0 2 * * *` |
| **Execute Command** | Run shell commands | Command + working directory |
| **PostgreSQL** | Database queries | Credentials + SQL query |
| **Function** | Custom JavaScript | Code to transform data |
| **IF** | Conditional routing | Condition to evaluate |
| **Wait** | Add delays | Duration in seconds |
| **Loop Over Items** | Iterate arrays | Array to loop over |

### Common Cron Schedules

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every hour | `0 * * * *` | At minute 0 |
| Every day at 2 AM | `0 2 * * *` | Daily scraping |
| Every 5 minutes | `*/5 * * * *` | Health checks |
| Every Monday at 9 AM | `0 9 * * 1` | Weekly tasks |
| First day of month | `0 0 1 * *` | Monthly cleanup |

---

## Data Flow Examples

### Example 1: Scraper Output

**Execute Command Node Output**:
```json
{
  "stdout": "Testing crawler...\nTesting scraper...\nTesting parser...\n✓ All tests passed\n✓ 10 items scraped\n✓ 10 records inserted",
  "stderr": "",
  "exitCode": 0
}
```

**Parse Results Node Output**:
```json
{
  "timestamp": "2025-10-26T15:00:00.000Z",
  "success": true,
  "items_scraped": 10,
  "items_inserted": 10,
  "output": "Testing crawler...",
  "errors": null,
  "status": "completed"
}
```

### Example 2: Database Query

**PostgreSQL Node Output**:
```json
[
  {
    "id": 1,
    "source_url": "https://quotes.toscrape.com",
    "raw_data": {
      "text": "Quote text",
      "author": "Author name",
      "tags": ["tag1", "tag2"]
    },
    "data_hash": "abc123...",
    "created_at": "2025-10-26T14:30:00.000Z"
  },
  {
    "id": 2,
    "source_url": "https://quotes.toscrape.com",
    "raw_data": {...},
    "data_hash": "def456...",
    "created_at": "2025-10-26T14:30:01.000Z"
  }
]
```

---

## Best Practices

### 1. Workflow Organization

```
Good Workflow Layout:
- Left to right flow
- Clear node names
- Related nodes grouped
- Notes for complex logic
```

### 2. Error Handling

```
Always Add:
- Error Trigger node
- Logging to database
- Notification on failure
- Retry logic where appropriate
```

### 3. Rate Limiting

```
Between Scraper Calls:
- Add Wait node
- Duration from config
- Respect robots.txt
- Monitor API quotas
```

### 4. Data Validation

```
Before Database Insert:
- Check required fields
- Validate data types
- Check for duplicates
- Transform if needed
```

---

## Quick Reference Commands

### View Workflow Files
```bash
dir n8n-workflows\*.json
```

### Edit Workflow JSON
```bash
notepad n8n-workflows\manual-test-scraper.json
```

### Import Workflow (via CLI - future)
```bash
npx n8n import:workflow --input=n8n-workflows/manual-test-scraper.json
```

---

**Created**: 2025-10-26
**For**: Intelligent Data Acquisition Platform
**n8n Version**: 1.116.2

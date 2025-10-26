# n8n Workflow Setup Instructions

## Quick Setup Guide

### Step 1: Access n8n Web Interface

1. Make sure n8n is running (if not, run `.\start-n8n.bat`)
2. Open your browser and go to: **http://localhost:5678**
3. You should see the n8n welcome screen

---

## Option A: Manual Workflow Creation (Recommended for Learning)

### Create "Manual Test Scraper" Workflow

#### 1. Create New Workflow
- Click **"+ New Workflow"** button in the top-right
- Name it: **"Manual Test Scraper"**

#### 2. Add Manual Trigger Node
- Click the **"+"** button on the canvas
- Search for **"Manual Trigger"**
- Click to add it

#### 3. Add Execute Command Node
- Click the **"+"** next to Manual Trigger
- Search for **"Execute Command"**
- Configure:
  - **Command**:
    ```bash
    cd "c:\Users\PUCCI\Desktop\gem\intelligent-data-platform" && python test_full_pipeline.py
    ```
- Click **"Execute Node"** to test

#### 4. Add PostgreSQL Node
- Click the **"+"** next to Execute Command
- Search for **"Postgres"**
- Click **"Create New Credential"**
- Configure credentials:
  ```
  Host: localhost
  Database: scraper_db
  User: scraper_user
  Password: 123456
  Port: 5432
  SSL: Disable
  ```
- Save credentials with name: **"Scraper Database"**
- Set operation: **"Execute Query"**
- Query:
  ```sql
  SELECT * FROM scraped_data
  ORDER BY created_at DESC
  LIMIT 10;
  ```

#### 5. Test the Workflow
- Click **"Execute Workflow"** button at the bottom
- Watch the nodes execute in sequence
- Green checkmarks = success!
- Click on each node to see the output

#### 6. Save the Workflow
- Click **"Save"** button in top-right
- Your workflow is now saved!

---

## Option B: Import Pre-Built Workflows

### Import Workflows via n8n UI

1. **Open n8n**: http://localhost:5678
2. **Click**: Workflows → Import from File
3. **Select files to import**:
   - `n8n-workflows/manual-test-scraper.json` - Simple test workflow
   - `n8n-workflows/scheduled-scraping-pipeline.json` - Automated daily scraper

4. **Configure PostgreSQL Credentials**:
   - Open the imported workflow
   - Click on any PostgreSQL node
   - Click **"Create New Credential"**
   - Enter:
     ```
     Host: localhost
     Database: scraper_db
     User: scraper_user
     Password: 123456
     Port: 5432
     SSL: Disable
     ```
   - Save as: **"Scraper Database"**

5. **Test the Workflow**:
   - For manual workflow: Click **"Execute Workflow"**
   - For scheduled workflow: Toggle **"Active"** switch to enable

---

## Available Workflows

### 1. Manual Test Scraper
**File**: `n8n-workflows/manual-test-scraper.json`

**Purpose**: Manual testing of the scraping pipeline

**Nodes**:
1. **Manual Trigger** - Click to run
2. **Run Test Pipeline** - Executes `test_full_pipeline.py`
3. **Fetch Latest Data** - Retrieves last 10 records from database

**How to Use**:
1. Open workflow in n8n
2. Click **"Execute Workflow"** button
3. View results in each node

---

### 2. Scheduled Scraping Pipeline
**File**: `n8n-workflows/scheduled-scraping-pipeline.json`

**Purpose**: Automated daily scraping with notifications

**Schedule**: Daily at 2:00 AM

**Nodes**:
1. **Schedule Trigger** - Runs at 2 AM daily
2. **Execute Scraper** - Runs test pipeline
3. **Parse Results** - Extracts success/failure info
4. **Verify Database** - Checks data was inserted
5. **Check Success** - Routes to success/error path
6. **Success Notification** - Shows success message
7. **Error Notification** - Shows error details

**How to Activate**:
1. Import workflow
2. Configure PostgreSQL credentials
3. Toggle **"Active"** switch at top
4. Workflow will run automatically at 2 AM

**Manual Test**:
- Click **"Execute Workflow"** to test immediately

---

## PostgreSQL Node Configuration

### Creating the Database Credential

1. **In any PostgreSQL node**, click **"Create New Credential"**
2. **Fill in the details**:
   ```
   Connection Type: Host
   Host: localhost
   Database: scraper_db
   User: scraper_user
   Password: 123456
   Port: 5432
   SSL: Disable
   ```
3. **Test Connection**: Click **"Test"** button
4. **Save**: Name it **"Scraper Database"**
5. **Reuse**: This credential can be used in all PostgreSQL nodes

---

## Common Queries for PostgreSQL Nodes

### 1. Fetch Pending Scraping Jobs
```sql
SELECT id, url, config_name, status
FROM scraping_queue
WHERE status = 'pending'
ORDER BY priority DESC, created_at ASC
LIMIT 10;
```

### 2. Get Latest Scraped Data
```sql
SELECT id, source_url, created_at,
       LEFT(raw_data::text, 100) as preview
FROM scraped_data
ORDER BY created_at DESC
LIMIT 20;
```

### 3. Count Records by Source
```sql
SELECT source_url, COUNT(*) as count
FROM scraped_data
GROUP BY source_url
ORDER BY count DESC;
```

### 4. Get Scraping Statistics
```sql
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT source_url) as unique_urls,
    MIN(created_at) as first_scrape,
    MAX(created_at) as last_scrape
FROM scraped_data;
```

### 5. Insert New Scraping Job
```sql
INSERT INTO scraping_queue (url, config_name, priority, status)
VALUES (
    'https://jumia.co.ke/phones/',
    'jumia_spa',
    5,
    'pending'
)
RETURNING id;
```

---

## Testing Your First Workflow

### Quick Test Steps

1. ✓ **n8n is running** (check http://localhost:5678)
2. ✓ **PostgreSQL is running** (check with `psql -U scraper_user -d scraper_db`)
3. **Import workflow** or create manually
4. **Configure PostgreSQL credentials**
5. **Click "Execute Workflow"**
6. **Check results**:
   - Execute Command node should show Python output
   - PostgreSQL node should show database records
   - All nodes should have green checkmarks

### Expected Results

**Execute Command Node Output**:
```
Testing crawler...
Testing scraper...
Testing parser...
Testing full pipeline...
✓ All tests passed
✓ Data inserted into database
```

**PostgreSQL Node Output**:
```json
[
  {
    "id": 1,
    "source_url": "https://quotes.toscrape.com",
    "raw_data": {...},
    "created_at": "2025-10-26T15:00:00.000Z"
  },
  ...
]
```

---

## Troubleshooting

### Workflow Won't Execute

**Problem**: Clicking "Execute Workflow" does nothing

**Solutions**:
1. Check if workflow is saved
2. Verify all nodes are connected (lines between nodes)
3. Check for red error indicators on nodes
4. Review execution log at bottom of screen

### PostgreSQL Connection Failed

**Problem**: "Connection failed" error

**Solutions**:
1. Verify PostgreSQL is running:
   ```bash
   psql -U scraper_user -d scraper_db
   ```
2. Check credentials are correct
3. Try `localhost` instead of `127.0.0.1`
4. Disable SSL in credential settings

### Execute Command Node Fails

**Problem**: "Command failed" or "File not found"

**Solutions**:
1. Check the path is correct
2. Use absolute path instead of relative:
   ```bash
   cd "c:\Users\PUCCI\Desktop\gem\intelligent-data-platform" && python test_full_pipeline.py
   ```
3. Verify Python is in PATH:
   ```bash
   python --version
   ```
4. Check file exists:
   ```bash
   dir test_full_pipeline.py
   ```

### No Data Returned from PostgreSQL

**Problem**: PostgreSQL query returns empty result

**Solutions**:
1. Check if data exists:
   ```sql
   SELECT COUNT(*) FROM scraped_data;
   ```
2. Run the test pipeline first:
   ```bash
   python test_full_pipeline.py
   ```
3. Verify table name is correct
4. Check query syntax

---

## Advanced Workflows

### Multi-Level Scraping Workflow

Create a workflow that:
1. Fetches URLs from database
2. Scrapes listing pages
3. For each product, scrapes detail page
4. Merges data and stores in database

**Nodes Needed**:
- Schedule Trigger
- PostgreSQL (fetch URLs)
- Loop Over Items
- Execute Command (scrape listing)
- Execute Command (scrape details)
- Code (merge data)
- PostgreSQL (insert results)

### Error Handling Workflow

Add error handling to workflows:
1. Add **"Error Trigger"** node
2. Connect to main workflow
3. Add **"Code"** node to format error
4. Add notification (future: Email/Slack)

---

## Next Steps

### After First Workflow Works

1. **Create more workflows** for different scrapers:
   - Jumia products scraper
   - Amazon products scraper
   - Jiji listings scraper

2. **Add scheduling**:
   - Daily scrapes at 2 AM
   - Hourly health checks
   - Weekly data cleanup

3. **Add monitoring**:
   - Database size checks
   - Scraping success rate
   - Error rate tracking

4. **Add notifications** (future):
   - Email alerts
   - Slack messages
   - Discord webhooks

---

## Workflow Best Practices

### 1. Always Test Manually First
- Use Manual Trigger before Schedule Trigger
- Execute each node individually
- Verify outputs at each step

### 2. Use Meaningful Names
- Name nodes clearly: "Fetch Pending Jobs", not "Postgres1"
- Name workflows descriptively
- Add notes to complex nodes

### 3. Error Handling
- Add Error Trigger nodes
- Log errors to database
- Send failure notifications

### 4. Rate Limiting
- Add Wait nodes between scraper calls
- Respect website rate limits
- Use configuration from YAML files

### 5. Data Validation
- Verify data before inserting
- Check for duplicates
- Validate required fields

---

## Resources

- **n8n Docs**: https://docs.n8n.io/
- **Node Reference**: https://docs.n8n.io/integrations/builtin/
- **Workflow Templates**: https://n8n.io/workflows/
- **Community Forum**: https://community.n8n.io/

---

## Success Checklist

- [ ] n8n is running at http://localhost:5678
- [ ] PostgreSQL credentials configured
- [ ] First workflow imported/created
- [ ] Workflow executed successfully
- [ ] Database shows scraped data
- [ ] Understand how to add/modify nodes
- [ ] Know how to schedule workflows
- [ ] Error handling in place

---

**Ready to automate!** 🚀

*For more details, see [N8N_INSTALLATION_COMPLETE.md](N8N_INSTALLATION_COMPLETE.md)*

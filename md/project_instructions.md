🔥 BRILLIANT IDEA! Using Gemini CLI to help build this project is actually very smart. Let me give you a complete prompt strategy.

📋 Master Prompt for Gemini CLI
Save this as project_instructions.md and feed it to Gemini:
markdown# Intelligent Data Acquisition Platform - Development Instructions

You are helping me build a production-grade web scraping and data acquisition platform for my computer science capstone project.

## PROJECT OVERVIEW

**Goal:** Build an intelligent, automated system that:
1. Crawls websites to discover URLs
2. Scrapes data from 100+ different websites
3. Uses AI (local LLM) to parse complex/unstructured data
4. Applies rule-based mapping and validation
5. Stores data in PostgreSQL
6. Provides REST API for data access
7. Monitors everything via Grafana dashboards
8. Orchestrates workflows with n8n

**Tech Stack:**
- Orchestration: n8n
- Backend: Python 3.11
- Scraping: BeautifulSoup, Playwright, Requests
- AI Parsing: Ollama + DeepSeek
- API: FastAPI
- Database: PostgreSQL
- Monitoring: Grafana + Prometheus
- Infrastructure: Docker Compose
- Deployment: VPS (8 vCPU, 32GB RAM)

**Target:** 100+ websites with different structures (HTML, SPA, API, PDF, Excel)

---

## ARCHITECTURE LAYERS

1. **Discovery Layer (Crawler)**
   - Auto-discovers URLs from seed URLs
   - Supports breadth-first, depth-first, priority-based crawling
   - Respects robots.txt and rate limits
   - Filters URLs based on patterns

2. **Extraction Layer (Scraper)**
   - Template-based architecture (5-7 templates for different site types)
   - Supports: HTML (static), SPA (JavaScript-rendered), REST APIs, PDFs, Excel
   - Config-driven (one YAML per site, not separate scripts)

3. **Parsing Layer**
   - CSS selector parser
   - XPath parser
   - JSON path parser
   - AI/LLM parser (for complex/unstructured data)
   - Auto-selects best parser based on data type

4. **Transformation Layer**
   - Field mapping (source → target schema)
   - Data cleaning and normalization
   - Type conversion
   - Validation and quality checks

5. **Storage Layer**
   - PostgreSQL for structured data
   - Redis for caching and queues
   - File storage for raw content

6. **API Layer**
   - RESTful endpoints for data access
   - Webhooks for triggering workflows
   - Health checks and statistics

7. **Monitoring Layer**
   - Grafana dashboards (system, scraping, quality metrics)
   - Prometheus metrics collection
   - Error tracking and alerting

---

## DESIGN PRINCIPLES

1. **Config-Driven Architecture**
   - NO separate script per site
   - ONE universal scraper engine
   - 5-7 scraper templates
   - 100+ YAML config files (one per site)

2. **Template-Based Scraping**
```
   Templates needed:
   - HTMLScraper (static sites)
   - SPAScraper (React/Vue/Angular sites using Playwright)
   - APIScraper (REST APIs)
   - PDFScraper (PDF documents)
   - ExcelScraper (Excel/CSV files)
```

3. **Separation of Concerns**
```
   Crawler → discovers URLs
   Scraper → fetches raw content
   Parser → extracts structured data
   Transformer → cleans and maps data
   Validator → ensures quality
   Storage → persists data
```

4. **Intelligent Fallbacks**
   - If CSS parser fails → try XPath
   - If both fail → use AI/LLM parser
   - If scraping fails → retry with backoff
   - If site blocks → log and continue

---

## PROJECT STRUCTURE
```
intelligent-data-platform/
├── crawler/
│   ├── crawler_engine.py
│   ├── sitemap_crawler.py
│   └── url_filter.py
├── scrapers/
│   ├── core/
│   │   ├── base_scraper.py
│   │   └── universal_scraper.py
│   └── templates/
│       ├── html_scraper.py
│       ├── spa_scraper.py
│       ├── api_scraper.py
│       ├── pdf_scraper.py
│       └── excel_scraper.py
├── parsers/
│   ├── parser_manager.py
│   ├── css_parser.py
│   ├── xpath_parser.py
│   ├── json_parser.py
│   └── ai_parser.py
├── transformers/
│   ├── data_transformer.py
│   └── field_mapper.py
├── validators/
│   ├── data_validator.py
│   └── quality_checker.py
├── pipeline/
│   └── crawler_scraper_pipeline.py
├── api/
│   ├── main.py
│   └── routers/
├── configs/
│   └── sites/ (100+ YAML files)
├── database/
│   └── schema.sql
├── n8n_workflows/
├── monitoring/
│   └── grafana/
└── docker-compose.yml
```

---

## DEVELOPMENT PHASES

### PHASE 1: Foundation (Week 1)

**Goal:** Build core crawler and scraper templates

**Tasks:**
1. Create base scraper abstract class
2. Implement HTMLScraper template (BeautifulSoup)
3. Implement SPAScraper template (Playwright for JS-rendered sites)
4. Implement APIScraper template
5. Build universal scraper engine that routes to correct template
6. Create crawler engine with URL discovery
7. Implement URL filtering and deduplication

**Key Files:**
- `scrapers/core/base_scraper.py` (~200 lines)
- `scrapers/templates/html_scraper.py` (~150 lines)
- `scrapers/templates/spa_scraper.py` (~200 lines)
- `scrapers/templates/api_scraper.py` (~100 lines)
- `scrapers/core/universal_scraper.py` (~150 lines)
- `crawler/crawler_engine.py` (~300 lines)

**Config Format Example:**
```yaml
name: "Example Site"
type: spa  # html, spa, api, pdf, excel
url: "https://example.com/products"

# Scraper settings
wait_for: ".product-card"
scroll: true

# Parser settings
parser_type: css
parser_config:
  container: ".product-card"
  fields:
    product_name: "h2.title::text"
    price: ".price::text"
    url: "a::attr(href)"
```

---

### PHASE 2: Parsing & Transformation (Week 2)

**Goal:** Extract and transform data intelligently

**Tasks:**
1. Build parser manager (auto-selects parser)
2. Implement CSS selector parser
3. Implement XPath parser
4. Implement JSON path parser (for APIs)
5. Integrate Ollama + DeepSeek for AI parsing
6. Build data transformer with field mapping
7. Create validation engine with rules

**Key Files:**
- `parsers/parser_manager.py` (~150 lines)
- `parsers/css_parser.py` (~180 lines)
- `parsers/xpath_parser.py` (~150 lines)
- `parsers/json_parser.py` (~120 lines)
- `parsers/ai_parser.py` (~200 lines)
- `transformers/data_transformer.py` (~150 lines)
- `validators/data_validator.py` (~120 lines)

**AI Parser Integration:**
```python
# Use Ollama API locally
POST http://localhost:11434/api/generate
{
  "model": "deepseek-coder:1.3b",
  "prompt": "Extract product_name, price, rating from: {text}"
}
```

---

### PHASE 3: Pipeline & Database (Week 2-3)

**Goal:** Connect all components and persist data

**Tasks:**
1. Build complete pipeline (crawler → scraper → parser → storage)
2. Design PostgreSQL schema for scraped data
3. Implement database connection and ORM models
4. Create batch insert functionality
5. Add URL state tracking (crawled, scraped, failed)
6. Implement change detection (detect when data updates)

**Key Files:**
- `pipeline/crawler_scraper_pipeline.py` (~200 lines)
- `database/schema.sql` (~300 lines)
- `database/connection.py` (~100 lines)

**Database Schema:**
```sql
CREATE TABLE scraped_data (
    id SERIAL PRIMARY KEY,
    source_url TEXT NOT NULL,
    source_site VARCHAR(100),
    product_name TEXT,
    price DECIMAL,
    scraped_at TIMESTAMP DEFAULT NOW(),
    data_hash VARCHAR(64),  -- for change detection
    raw_data JSONB
);

CREATE TABLE crawl_state (
    url TEXT PRIMARY KEY,
    status VARCHAR(20),  -- pending, completed, failed
    last_crawled TIMESTAMP,
    retry_count INT DEFAULT 0
);
```

---

### PHASE 4: REST API (Week 3)

**Goal:** Provide programmatic access to data

**Tasks:**
1. Set up FastAPI application
2. Create data access endpoints (GET, filter, search)
3. Add statistics endpoints
4. Implement webhook endpoints for n8n
5. Add authentication (optional but good for demo)
6. Generate OpenAPI documentation

**Key Files:**
- `api/main.py` (~150 lines)
- `api/routers/data.py` (~200 lines)
- `api/routers/webhooks.py` (~100 lines)

**API Endpoints:**
```
GET  /api/v1/data              - List scraped data
GET  /api/v1/data/{id}         - Get single record
GET  /api/v1/stats             - System statistics
POST /api/v1/trigger/{site}    - Trigger scraping
GET  /api/v1/health            - Health check
```

---

### PHASE 5: n8n Integration (Week 3)

**Goal:** Automate workflows

**Tasks:**
1. Create n8n workflows for:
   - Daily scheduled scraping
   - Error handling and retries
   - Data quality checks
   - Notifications (Slack/email)
2. Export workflows as JSON
3. Document workflow logic

**Workflows Needed:**
- `main_pipeline.json` - Main scraping workflow
- `error_handler.json` - Retry failed scrapes
- `quality_checker.json` - Validate data quality
- `monitoring.json` - Collect metrics

---

### PHASE 6: Monitoring (Week 3-4)

**Goal:** Observability and metrics

**Tasks:**
1. Set up Prometheus metrics collection
2. Create Grafana dashboards:
   - System overview (CPU, RAM, disk)
   - Scraping metrics (success rate, pages/min)
   - Data quality (validation errors, missing fields)
   - API performance (response times)
3. Configure alerts for failures

**Grafana Dashboards:**
- System Overview
- Scraping Performance
- Data Quality
- API Metrics

---

### PHASE 7: Site Configs (Week 4)

**Goal:** Configure 100 sites

**Tasks:**
1. Create template configs for different site types
2. Generate 100 YAML configs (can use AI to help)
3. Test each config
4. Document config format

**Config Template:**
```yaml
name: "Site Name"
type: html  # or spa, api, pdf, excel

# Crawler settings
seed_url: "https://site.com"
url_patterns: ["/products/", "/items/"]
exclude_patterns: ["/about", "/contact"]
max_depth: 2

# Scraper settings
wait_for: ".container"  # for SPA
scroll: false

# Parser settings
parser_type: css
parser_config:
  container: ".item"
  fields:
    title: "h2::text"
    price: ".price::text"

# Transformation
transformations:
  price:
    - strip: "$"
    - convert: float
```

---

### PHASE 8: Docker & Deployment (Week 4)

**Goal:** Production-ready deployment

**Tasks:**
1. Create docker-compose.yml with all services
2. Write Dockerfiles for custom services
3. Set up nginx reverse proxy
4. Configure environment variables
5. Create deployment scripts
6. Write backup scripts

**docker-compose.yml services:**
```yaml
services:
  n8n:
  postgres:
  redis:
  ollama:
  api:
  grafana:
  prometheus:
  nginx:
```

---

### PHASE 9: Documentation (Week 4)

**Goal:** Complete documentation for capstone

**Tasks:**
1. Write comprehensive README
2. Create architecture diagrams
3. Write API documentation
4. Create user guide
5. Write capstone report (academic paper)
6. Prepare presentation slides

**Documents Needed:**
- README.md (setup instructions)
- architecture.md (system design)
- api-documentation.md (API specs)
- capstone-report.pdf (academic paper)
- presentation.pptx (defense slides)

---

## CODE GENERATION GUIDELINES

When generating code, follow these principles:

1. **Type Hints:** Always use Python type hints
```python
   def scrape(url: str) -> List[Dict[str, Any]]:
```

2. **Error Handling:** Wrap in try-except, never fail silently
```python
   try:
       data = scrape()
   except Exception as e:
       logger.error(f"Scraping failed: {e}")
       return None
```

3. **Logging:** Use structured logging
```python
   logger.info(f"Scraped {len(items)} items from {url}")
```

4. **Configuration:** Load from YAML, never hardcode
```python
   config = yaml.load(open('config.yaml'))
```

5. **Modularity:** Small functions, single responsibility
```python
   def extract_price(element): ...
   def clean_price(raw_price): ...
   def validate_price(price): ...
```

6. **Documentation:** Docstrings for all classes/functions
```python
   def scrape(url: str) -> List[Dict]:
       """
       Scrape data from given URL
       
       Args:
           url: Target URL to scrape
           
       Returns:
           List of extracted items as dictionaries
       """
```

---

## SPECIFIC IMPLEMENTATION REQUESTS

When I ask you to generate code, please:

1. **For Scrapers:** Include proper wait times, error handling, and retry logic
2. **For Parsers:** Support both simple and complex selectors
3. **For AI Integration:** Show complete Ollama API integration
4. **For Database:** Include migrations and proper indexing
5. **For API:** Include request validation with Pydantic models
6. **For Configs:** Show multiple real-world examples

---

## TESTING REQUIREMENTS

Generate tests that:
1. Use pytest framework
2. Mock external requests
3. Test happy path and edge cases
4. Include integration tests for full pipeline
5. Achieve >80% code coverage

---

## PERFORMANCE CONSIDERATIONS

1. **Parallelization:** Use batching for multiple scrapers
2. **Caching:** Redis for frequently accessed data
3. **Rate Limiting:** Respect politeness delays
4. **Connection Pooling:** Reuse HTTP sessions
5. **Async Operations:** Use asyncio where appropriate

---

## ACADEMIC REQUIREMENTS

This is a capstone project, so emphasize:
1. **Software design patterns** (Factory, Strategy, Observer)
2. **Scalability** (handles 100+ sites, 1000+ pages)
3. **Reliability** (error handling, retries, monitoring)
4. **Performance** (metrics, optimization)
5. **Documentation** (architecture, API, user guide)

---

## SUCCESS CRITERIA

The project is complete when:
- ✅ 100 sites configured and working
- ✅ All 5 scraper templates implemented
- ✅ AI parser integrated with Ollama
- ✅ REST API with 90%+ uptime
- ✅ Grafana dashboards showing metrics
- ✅ n8n workflows running automatically
- ✅ Full documentation written
- ✅ Tests passing with >80% coverage
- ✅ Deployed on VPS and accessible

---

## IMPORTANT CONSTRAINTS

1. **NO localStorage/sessionStorage** in any artifacts (not supported)
2. **Local-first architecture** (avoid cloud dependencies)
3. **Template-based design** (NOT 100 separate scripts)
4. **Config-driven** (YAML configs, not hardcoded)
5. **Production-grade** (error handling, logging, monitoring)

---

## WHEN HELPING ME

Please:
1. Ask clarifying questions before generating large code blocks
2. Provide complete, working code (not pseudocode)
3. Include error handling and logging
4. Add comments explaining complex logic
5. Suggest improvements and best practices
6. Warn about potential issues or bottlenecks

---

## CURRENT STATUS

I'm at: [UPDATE THIS as you progress]
- [ ] Phase 1: Foundation
- [ ] Phase 2: Parsing
- [ ] Phase 3: Pipeline
- [ ] Phase 4: API
- [ ] Phase 5: n8n
- [ ] Phase 6: Monitoring
- [ ] Phase 7: Configs
- [ ] Phase 8: Deployment
- [ ] Phase 9: Documentation

Next task: [DESCRIBE what you need help with]

---

END OF INSTRUCTIONS
# Intelligent Data Acquisition Platform

## Project Overview

The Intelligent Data Acquisition Platform is a robust, automated system designed for web scraping and data acquisition. It intelligently crawls websites, extracts structured and unstructured data, processes it using AI and rule-based transformations, stores it in PostgreSQL, and provides API access. The entire system is orchestrated with n8n and monitored via Grafana and Prometheus.

## Features

-   **Intelligent Crawling:** Auto-discovers URLs with BFS/DFS strategies, respects `robots.txt`, and applies rate limits.
-   **Flexible Scraping:** Supports HTML (static), SPA (JavaScript-rendered), API, PDF, and Excel sites using a template-based, config-driven approach.
-   **Advanced Parsing:** Utilizes CSS selectors, XPath, and AI (Gemini API) for robust data extraction.
-   **Data Transformation:** Field mapping, type conversion, and data cleaning.
-   **Data Validation:** Rule-based validation engine to ensure data quality.
-   **Persistent Storage:** PostgreSQL database for structured data, Redis for caching and queues.
-   **RESTful API:** FastAPI-based API for data access, site management, and webhook integration.
-   **Workflow Orchestration:** n8n integration for scheduled tasks, error handling, and notifications.
-   **Comprehensive Monitoring:** Grafana dashboards for system, scraping, and API metrics, powered by Prometheus.
-   **Containerized Deployment:** Docker Compose for easy setup and deployment.
-   **Change Detection:** Data hashing to detect and manage updates in scraped content.

## Tech Stack

-   **Orchestration:** n8n
-   **Backend:** Python 3.11 (FastAPI, BeautifulSoup, Playwright, SQLAlchemy, lxml, prometheus_client)
-   **AI Parsing:** Gemini API
-   **Database:** PostgreSQL, Redis
-   **Monitoring:** Grafana, Prometheus, Node Exporter, Postgres Exporter, Redis Exporter
-   **Infrastructure:** Docker Compose

## Architecture

The platform is built with a layered architecture to ensure separation of concerns:

1.  **Discovery Layer (Crawler):** Identifies and manages URLs to be scraped.
2.  **Extraction Layer (Scraper):** Fetches raw content from various website types.
3.  **Parsing Layer:** Extracts structured data from raw content using various parsers (CSS, XPath, AI).
4.  **Transformation Layer:** Cleans, normalizes, and maps extracted data.
5.  **Validation Layer:** Ensures the quality and integrity of the data.
6.  **Storage Layer:** Persists processed data into PostgreSQL.
7.  **API Layer:** Provides programmatic access and control over the platform.
8.  **Monitoring Layer:** Observability through metrics and alerts.
9.  **Orchestration Layer:** Automates workflows and tasks with n8n.

## Getting Started

Follow these steps to set up and run the platform on your local machine or a VPS.

### Prerequisites

-   **Git:** For cloning the repository.
-   **Docker & Docker Compose:** For containerized deployment.
-   **Gemini API Key:** Obtain a Gemini API key from Google AI Studio. Set it as an environment variable `GEMINI_API_KEY`.

### 1. Clone the Repository

```bash
git clone YOUR_GIT_REPOSITORY_URL
cd intelligent-data-platform
```
**Note:** Replace `YOUR_GIT_REPOSITORY_URL` with the actual URL of your Git repository.

### 2. Setup Environment Variables

Create a `.env` file in the root of the `intelligent-data-platform` directory. You can use the `deployment.sh` script to help with this, or create it manually.

**Example `.env` content:**
```
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://gemini:your_secure_password@postgres:5432/idp_data
REDIS_URL=redis://redis:6379
OPENWEATHERMAP_API_KEY=YOUR_OPENWEATHERMAP_API_KEY # Required for weather_api_json.yml example
```
**Important:** Replace `your_secure_password` and `YOUR_OPENWEATHERMAP_API_KEY` with your actual values.

### 3. Deploy with Docker Compose

Navigate to the `intelligent-data-platform` directory and run Docker Compose:

```bash
docker-compose build
docker-compose up -d
```
This will build the API service image and start all defined services (PostgreSQL, Redis, Ollama, n8n, Prometheus, Grafana, API, Nginx, and various exporters).

### 4. Initial Database Setup

Once PostgreSQL is running, you need to create the database schema. You can do this by executing the `schema.sql` file.

```bash
docker exec -it idp_postgres psql -U gemini -d idp_data -f /docker-entrypoint-initdb.d/schema.sql
# Note: The schema.sql is typically copied into /docker-entrypoint-initdb.d/ by Dockerfile if placed there.
# For manual execution, you might need to copy it into the container or run from host:
# docker cp database/schema.sql idp_postgres:/tmp/schema.sql
# docker exec -it idp_postgres psql -U gemini -d idp_data -f /tmp/schema.sql
```
**Alternatively, you can use a Python script to create tables:**
```bash
# From the intelligent-data-platform directory
python -c "from intelligent_data_platform.database.connection import create_all_tables; create_all_tables()"
```

### 5. Import n8n Workflows

Access your n8n instance (usually at `http://localhost/n8n` or `http://your_vps_ip/n8n`).
-   Go to "Workflows" -> "New" -> "Import from JSON".
-   Import `n8n_workflows/main_pipeline.json`, `n8n_workflows/error_handler.json`, and `n8n_workflows/quality_checker.json`.
-   Activate the workflows.

### 6. Import Grafana Dashboards

Access your Grafana instance (usually at `http://localhost/grafana` or `http://your_vps_ip/grafana`). Default credentials are `admin`/`admin`.
-   Go to "Dashboards" -> "Import".
-   Upload `monitoring/grafana/scraping_dashboard.json` and `monitoring/grafana/system_overview_dashboard.json`.
-   Ensure the Prometheus datasource is configured (it should be automatically if using Docker Compose).

## Usage

### Accessing Services

-   **Nginx (Reverse Proxy):** `http://localhost` or `http://your_vps_ip`
-   **FastAPI API Docs:** `http://localhost/api/v1/docs` or `http://your_vps_ip/api/v1/docs`
-   **Grafana:** `http://localhost/grafana` or `http://your_vps_ip/grafana`
-   **n8n:** `http://localhost/n8n` or `http://your_vps_ip/n8n`

### Managing Sites via API

Use the FastAPI interactive documentation (`/api/v1/docs`) to:
-   **Create Sites:** `POST /api/v1/sites` with your site configuration details.
-   **List Sites:** `GET /api/v1/sites`
-   **Trigger Scrapes:** `POST /api/v1/trigger/{site_name}`

### Site Configuration

Site-specific scraping rules are defined in YAML files located in `configs/sites/`. You can use the `config_generator.py` script to help create these.

## Monitoring

Prometheus collects metrics from all services, and Grafana provides dashboards for visualization.
-   **Prometheus UI:** `http://localhost:9090` (or `http://your_vps_ip:9090`)
-   **Grafana Dashboards:** Access via Nginx at `/grafana`.

## Backup

Use the `backup.sh` script to create and manage PostgreSQL database backups.

```bash
./backup.sh
```
Consider scheduling this script with `cron` for automated daily backups.

## Contributing

(Placeholder for contribution guidelines)

## License

(Placeholder for license information)

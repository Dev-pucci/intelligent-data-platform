# User Guide: Adding New Sites to the Platform

This guide provides step-by-step instructions on how to add a new website to the Intelligent Data Acquisition Platform for scraping. The platform uses a config-driven approach, meaning you define how to scrape a site using a YAML configuration file.

## 1. Overview of Site Configuration

The platform's flexibility comes from its YAML configuration files, located in `configs/sites/`. Each file defines the rules for crawling, scraping, parsing, transforming, and validating data from a specific website.

A typical site configuration includes:
-   **General Information:** `name`, `type` (html, spa, api, pdf, excel), `seed_url`.
-   **Crawler Settings:** Rules for discovering URLs.
-   **Scraper Settings:** How to interact with the webpage (e.g., `wait_for`, `scroll`).
-   **Parser Settings:** How to extract structured data (`parser_type`, `parser_config` with selectors/expressions).
-   **Transformation Rules:** How to clean and normalize data.
-   **Validation Rules:** How to ensure data quality.

## 2. Steps to Add a New Site

### Step 1: Analyze the Target Website

Before creating a configuration, spend some time understanding the target website:
-   **Identify Site Type:** Is it a static HTML site, a JavaScript-rendered SPA, an API, or does it offer PDF/Excel files? This determines your `type` in the config.
-   **Identify Seed URL:** What's the starting URL for the crawler/scraper?
-   **Inspect HTML/Network:** Use browser developer tools to identify stable CSS selectors or XPath expressions for the data you want to extract. Look for `id` attributes, `data-*` attributes, or unique structural patterns. For APIs, understand the request/response structure.

### Step 2: Generate or Create the YAML Configuration File

You have two primary ways to create the YAML configuration file:

#### Option A: Using the `config_generator.py` Script (Recommended)

The `config_generator.py` script uses AI to suggest initial parsing rules, making the process faster.

1.  **Ensure Ollama is Running:** Make sure your Ollama server is active and the `deepseek-coder:1.3b` model is pulled.
2.  **Run the Script:**
    ```bash
    python config_generator.py --url "https://www.example.com/target-page" --name "MyExampleSite"
    ```
    -   Replace `"https://www.example.com/target-page"` with the actual URL.
    -   Replace `"MyExampleSite"` with a unique name for your site.
3.  **Review and Refine:** The script will generate a YAML file in `configs/sites/`. Open this file and carefully review the suggested `parser_config`. Adjust selectors, add transformation rules, and define validation rules as needed.

#### Option B: Manually Creating from a Template

1.  **Choose a Template:** Start with an existing example or a template like `configs/sites/ecommerce_template.yml`.
2.  **Copy and Rename:** Copy the chosen template to a new file in `configs/sites/` (e.g., `my_new_site.yml`).
3.  **Edit the File:** Open the new YAML file and fill in the details based on your website analysis from Step 1. Pay close attention to:
    -   `name`: A unique identifier for your site.
    -   `type`: `html`, `spa`, `api`, `pdf`, or `excel`.
    -   `seed_url`: The starting URL.
    -   `crawler_settings`: Define `url_patterns` and `exclude_patterns` to guide the crawler.
    -   `scraper_settings`: Add `wait_for` (for SPAs) or `headers` (for APIs).
    -   `parser_type`: `css`, `xpath`, `json`, or `ai`.
    -   `parser_config`: Define `container` and `fields` with appropriate selectors/expressions.
    -   `transformations`: Add rules to clean and convert data types.
    -   `validation_rules`: Define rules to ensure data quality.

### Step 3: Add the Site to the Platform via API

Once your YAML configuration file is ready and saved in `configs/sites/`, you need to register it with the platform's API.

1.  **Access API Docs:** Open your browser to `http://localhost/api/v1/docs` (or your deployed API URL).
2.  **Use `POST /api/v1/sites`:**
    -   Click on the `POST /api/v1/sites` endpoint.
    -   Click "Try it out".
    -   Fill in the `SiteConfigCreate` request body:
        ```json
        {
          "name": "MyExampleSite",
          "config_file_path": "configs/sites/my_new_site.yml", # Path relative to project root
          "is_active": true
        }
        ```
    -   Click "Execute".
3.  **Verify:** A successful response will return the created `SiteConfig` object, including its `site_id`. You can also use `GET /api/v1/sites` to see if your site is listed.

### Step 4: Verify and Test (Manual Scrape)

To quickly test your new site configuration:

1.  **Access API Docs:** Go to `http://localhost/api/v1/docs`.
2.  **Use `POST /api/v1/trigger/{site_name}`:**
    -   Click on the `POST /api/v1/trigger/{site_name}` endpoint.
    -   Click "Try it out".
    -   Enter your `site_name` (e.g., "MyExampleSite").
    -   Optionally, provide a specific `url` in the request body if you want to test a single page instead of the `seed_url`.
    -   Click "Execute".
3.  **Check Logs:** Monitor the Docker Compose logs (`docker-compose logs -f api`) for messages from the scraper and parser.
4.  **Check Database:** Query the `scraped_data` table in PostgreSQL to see if data was inserted.

### Step 5: Integrate with n8n (Optional)

For automated, scheduled scraping, integrate your new site with n8n:

1.  **Access n8n:** Go to `http://localhost/n8n`.
2.  **Modify `main_pipeline.json`:**
    -   Open the "Daily Scheduled Scraping Pipeline" workflow.
    -   Modify the "Trigger Scrape API" HTTP Request node to call your new site's trigger endpoint (e.g., `http://localhost:8000/api/v1/webhooks/trigger/MyExampleSite`).
    -   Consider adding logic to iterate through all active sites from the API.
3.  **Activate:** Ensure the workflow is active.

## 3. Tips for Robust Selectors

-   **Partial CSS Selectors:** Use `[class*="partial-name"]` or `[class^="start-name"]` for dynamic class names.
-   **Stable Attributes:** Prefer `id` attributes or `data-*` attributes (e.g., `div[data-testid="price"]`).
-   **XPath:** For complex navigation or text-based selection, use XPath (e.g., `//div[contains(text(), 'Price:')]/following-sibling::span`).
-   **AI Parser:** For highly unstructured content, use `parser_type: ai` and provide a clear `prompt_template`.

## 4. Troubleshooting Common Issues

-   **`ModuleNotFoundError` in Docker:** Ensure all Python dependencies are in `requirements.txt` and `docker-compose build` was run.
-   **Scraper Fails to Fetch:** Check `seed_url`, network connectivity, `robots.txt` rules, and `scraper_settings` (e.g., `wait_for` for SPAs).
-   **Parser Fails to Extract:** Verify CSS/XPath selectors using browser developer tools. Check `parser_type` and `parser_config`.
-   **Ollama Connection Issues:** Ensure Ollama container is running and the model is pulled.
-   **Database Errors:** Check `DATABASE_URL` in `.env` and PostgreSQL container logs.

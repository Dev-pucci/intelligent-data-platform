# Intelligent Data Acquisition Platform - API Documentation

## 1. Introduction

This document provides a human-readable overview and examples for interacting with the Intelligent Data Acquisition Platform's RESTful API. The API allows for programmatic access to scraped data, management of site configurations, and integration with external systems like n8n via webhooks.

For interactive API documentation (Swagger UI), please visit `/api/v1/docs` when the API is running.

## 2. Base URL

The base URL for all API endpoints is: `http://localhost:8000/api/v1` (or `http://your_vps_ip:8000/api/v1` if deployed).

## 3. Authentication

*(Authentication is not yet implemented. This section will be updated once authentication mechanisms are in place.)*

## 4. Endpoints

### 4.1. Data Endpoints (`/data`)

These endpoints allow you to retrieve and query the scraped data.

#### `GET /data` - List Scraped Data

Retrieves a list of scraped data records with optional filtering, searching, and pagination.

-   **Query Parameters:**
    -   `skip` (integer, optional): Number of items to skip (for pagination). Default: `0`.
    -   `limit` (integer, optional): Maximum number of items to return (for pagination). Default: `100`.
    -   `product_name` (string, optional): Filter by product name (case-insensitive partial match).
    -   `min_price` (float, optional): Filter by minimum price.
    -   `max_price` (float: optional): Filter by maximum price.
    -   `source_url` (string, optional): Filter by source URL (case-insensitive partial match).
    -   `q` (string, optional): General search query across product name and source URL.

-   **Example Request:**
    ```
    GET /api/v1/data?limit=10&product_name=laptop&min_price=500&q=pro
    ```

-   **Example Response (200 OK):**
    ```json
    [
      {
        "id": 1,
        "source_url": "http://example.com/product/1",
        "product_name": "Laptop Pro",
        "price": 1200.5,
        "scraped_at": "2023-10-26T10:00:00.000Z",
        "data_hash": "a1b2c3d4e5f6...",
        "raw_data": {
          "original_title": "Laptop Pro 15-inch",
          "original_price_text": "$1,200.50"
        }
      }
    ]
    ```

#### `GET /data/{id}` - Get Single Scraped Record

Retrieves a single scraped data record by its unique ID.

-   **Path Parameters:**
    -   `id` (integer, required): The ID of the scraped data record.

-   **Example Request:**
    ```
    GET /api/v1/data/1
    ```

-   **Example Response (200 OK):**
    ```json
    {
      "id": 1,
      "source_url": "http://example.com/product/1",
      "product_name": "Laptop Pro",
      "price": 1200.5,
      "scraped_at": "2023-10-26T10:00:00.000Z",
      "data_hash": "a1b2c3d4e5f6...",
      "raw_data": {
        "original_title": "Laptop Pro 15-inch",
        "original_price_text": "$1,200.50"
      }
    }
    ```

### 4.2. Site Management Endpoints (`/sites`)

These endpoints allow you to manage the configurations of websites to be scraped.

#### `POST /sites` - Create New Site Configuration

Creates a new site configuration record in the database.

-   **Request Body (`SiteConfigCreate`):**
    ```json
    {
      "name": "My New E-commerce Site",
      "config_file_path": "/path/to/configs/sites/my_new_ecommerce.yml",
      "is_active": true
    }
    ```

-   **Example Response (201 Created):**
    ```json
    {
      "name": "My New E-commerce Site",
      "config_file_path": "/path/to/configs/sites/my_new_ecommerce.yml",
      "is_active": true,
      "site_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "created_at": "2023-10-26T10:00:00.000Z",
      "updated_at": "2023-10-26T10:00:00.000Z"
    }
    ```

#### `GET /sites` - List Site Configurations

Retrieves a list of all registered site configurations.

-   **Query Parameters:** `skip` (integer, optional), `limit` (integer, optional)

-   **Example Request:**
    ```
    GET /api/v1/sites?limit=5
    ```

#### `GET /sites/{site_id}` - Get Single Site Configuration

Retrieves a single site configuration by its unique ID.

-   **Path Parameters:**
    -   `site_id` (string, required): The UUID of the site configuration.

-   **Example Request:**
    ```
    GET /api/v1/sites/a1b2c3d4-e5f6-7890-1234-567890abcdef
    ```

#### `PUT /sites/{site_id}` - Update Site Configuration

Updates an existing site configuration.

-   **Path Parameters:**
    -   `site_id` (string, required): The UUID of the site configuration.
-   **Request Body (`SiteConfigCreate`):** (Same as `POST /sites`)

-   **Example Request:**
    ```
    PUT /api/v1/sites/a1b2c3d4-e5f6-7890-1234-567890abcdef
    Content-Type: application/json

    {
      "name": "My Updated E-commerce Site",
      "config_file_path": "/path/to/configs/sites/my_updated_ecommerce.yml",
      "is_active": false
    }
    ```

#### `DELETE /sites/{site_id}` - Delete Site Configuration

Deletes a site configuration by its unique ID.

-   **Path Parameters:**
    -   `site_id` (string, required): The UUID of the site configuration.

-   **Example Request:**
    ```
    DELETE /api/v1/sites/a1b2c3d4-e5f6-7890-1234-567890abcdef
    ```

-   **Example Response (204 No Content):** (No response body)

### 4.3. Webhook Endpoints (`/webhooks`)

These endpoints are primarily designed for integration with n8n or other external systems to trigger actions or receive data.

#### `POST /webhooks/trigger/{site_name}` - Trigger Scraping Task

Triggers a scraping task for a specified site.

-   **Path Parameters:**
    -   `site_name` (string, required): The name of the site to scrape.
-   **Request Body (`ScrapeTriggerRequest`):**
    ```json
    {
      "site_name": "TechCrunch Blog",
      "url": "https://techcrunch.com/latest-article",
      "job_parameters": {
        "priority": "high"
      }
    }
    ```

-   **Example Response (200 OK):**
    ```json
    {
      "message": "Scraping for site 'TechCrunch Blog' triggered successfully.",
      "status": "received",
      "details": {
        "site_name": "TechCrunch Blog",
        "url": "https://techcrunch.com/latest-article",
        "job_parameters": {
          "priority": "high"
        }
      }
    }
    ```

#### `POST /webhooks/status_update` - Receive Status Update

Receives status updates for jobs or processes.

-   **Request Body (`StatusUpdate`):**
    ```json
    {
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "completed",
      "message": "Scraping job finished successfully.",
      "items_processed": 150
    }
    ```

#### `POST /webhooks/data_injest` - Ingest Data

Receives data for direct ingestion into the platform.

-   **Request Body (`DataIngest`):**
    ```json
    {
      "site_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "data": [
        {
          "product_name": "Sample Product 1",
          "price": 29.99,
          "source_url": "http://example.com/product/sample1"
        },
        {
          "product_name": "Sample Product 2",
          "price": 49.99,
          "source_url": "http://example.com/product/sample2"
        }
      ]
    }
    ```

### 4.4. Monitoring Endpoints

These endpoints provide health checks and system statistics.

#### `GET /health` - Health Check

Returns the health status of the API.

-   **Example Request:**
    ```
    GET /api/v1/health
    ```

-   **Example Response (200 OK):**
    ```json
    {
      "status": "ok"
    }
    ```

#### `GET /stats` - System Statistics

Returns various system statistics (placeholder data for now).

-   **Example Request:**
    ```
    GET /api/v1/stats
    ```

-   **Example Response (200 OK):**
    ```json
    {
      "total_sites_configured": 100,
      "sites_scraped_today": 15,
      "total_records": 10234,
      "crawler_status": "idle"
    }
    ```

#### `GET /metrics` - Prometheus Metrics

Exposes Prometheus metrics in a format that can be scraped by a Prometheus server.

-   **Example Request:**
    ```
    GET /metrics
    ```

-   **Example Response (200 OK):**
    ```
    # HELP scraper_requests_total Total number of scrape requests
    # TYPE scraper_requests_total counter
    scraper_requests_total{site="ExampleSite",status="triggered",type="unknown"} 1.0
    # HELP api_requests_total Total number of API requests
    # TYPE api_requests_total counter
    api_requests_total{endpoint="/api/v1/trigger/{site_name}",status_code="200"} 1.0
    # ... other Prometheus metrics ...
    ```

## 5. Pydantic Models

The API extensively uses Pydantic models (defined in `api/schemas.py`) for automatic request body validation, response serialization, and clear data contracts. Key models include:
-   `ScrapedDataItem`: Represents a single scraped data record.
-   `SiteConfigCreate`: Used for creating/updating site configurations.
-   `SiteConfig`: Represents a full site configuration with database-generated fields.
-   `ScrapeTriggerRequest`: Defines the payload for triggering scraping jobs via webhooks.
-   `StatusUpdate`: Defines the payload for receiving status updates.
-   `DataIngest`: Defines the payload for ingesting data directly into the platform.

## 6. Error Handling

The API returns standard HTTP status codes for errors (e.g., `404 Not Found`, `422 Unprocessable Entity` for validation errors). Error responses typically include a `detail` field with a descriptive message.

## 7. Future Enhancements

-   Implement user authentication and authorization.
-   Add more detailed filtering and search options.
-   Integrate with a task queue for asynchronous job processing.

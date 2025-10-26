-- schema.sql for the Intelligent Data Acquisition Platform

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- Table for managing configured sites
-- =============================================================================
CREATE TABLE sites (
    site_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    config_file_path TEXT NOT NULL, -- Path to the YAML config file
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE sites IS 'Stores metadata about each configured website to be scraped.';
COMMENT ON COLUMN sites.name IS 'Unique name for the site, e.g., "TechCrunch Blog".';


-- =============================================================================
-- Table for tracking crawl state of URLs
-- =============================================================================
CREATE TABLE crawl_state (
    url TEXT PRIMARY KEY,
    site_id UUID REFERENCES sites(site_id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'in_progress')),
    last_crawled TIMESTAMP WITH TIME ZONE,
    retry_count INT DEFAULT 0,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_crawl_state_status ON crawl_state(status);
CREATE INDEX idx_crawl_state_site_id ON crawl_state(site_id);

COMMENT ON TABLE crawl_state IS 'Tracks the crawling status of every URL discovered.';
COMMENT ON COLUMN crawl_state.status IS 'The current state of the URL in the crawl queue.';


-- =============================================================================
-- Table for logging scrape job executions
-- =============================================================================
CREATE TABLE scrape_jobs (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('started', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    items_scraped INT DEFAULT 0,
    log_summary TEXT -- For storing a summary of logs or errors
);

CREATE INDEX idx_scrape_jobs_site_id ON scrape_jobs(site_id);
CREATE INDEX idx_scrape_jobs_status ON scrape_jobs(status);

COMMENT ON TABLE scrape_jobs IS 'Logs each execution of a scraping job for a site.';


-- =============================================================================
-- Main table for storing structured, scraped data
-- =============================================================================
CREATE TABLE scraped_data (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES scrape_jobs(job_id) ON DELETE SET NULL,
    site_id UUID REFERENCES sites(site_id) ON DELETE SET NULL,
    source_url TEXT NOT NULL UNIQUE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Dynamic data fields (examples)
    product_name TEXT,
    price DECIMAL(10, 2),
    
    data_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of the data to detect changes
    raw_data JSONB -- Store the original, unprocessed data from the parser
);

CREATE INDEX idx_scraped_data_source_url ON scraped_data(source_url);
CREATE INDEX idx_scraped_data_data_hash ON scraped_data(data_hash);
CREATE INDEX idx_scraped_data_site_id ON scraped_data(site_id);
CREATE INDEX idx_scraped_data_scraped_at ON scraped_data(scraped_at);

COMMENT ON TABLE scraped_data IS 'The main repository for cleaned and structured data extracted from websites.';
COMMENT ON COLUMN scraped_data.data_hash IS 'SHA-256 hash of the item data, used for change detection.';
COMMENT ON COLUMN scraped_data.raw_data IS 'The complete, structured data for the item as a JSON object.';


-- =============================================================================
-- Table for logging data quality issues
-- =============================================================================
CREATE TABLE data_quality_issues (
    issue_id SERIAL PRIMARY KEY,
    scraped_data_id INT NOT NULL REFERENCES scraped_data(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    issue_type VARCHAR(100) NOT NULL, -- e.g., 'missing_value', 'invalid_format'
    details TEXT,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_data_quality_issues_scraped_data_id ON data_quality_issues(scraped_data_id);
CREATE INDEX idx_data_quality_issues_issue_type ON data_quality_issues(issue_type);

COMMENT ON TABLE data_quality_issues IS 'Logs any validation errors or quality issues found in the scraped data.';

-- =============================================================================
-- Function to automatically update `updated_at` timestamps
-- =============================================================================
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the trigger to the sites table
CREATE TRIGGER set_sites_timestamp
BEFORE UPDATE ON sites
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

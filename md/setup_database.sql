-- Setup script for Intelligent Data Platform database

-- Create user
CREATE USER gemini WITH PASSWORD 'password';

-- Create database
CREATE DATABASE idp_data OWNER gemini;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE idp_data TO gemini;

-- Connect to the database
\c idp_data

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO gemini;

-- Display success message
SELECT 'Database setup completed successfully!' AS status;

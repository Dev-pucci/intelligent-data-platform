#!/bin/bash

# backup.sh - Script to backup the PostgreSQL database

# --- Configuration ---
DB_CONTAINER_NAME="idp_postgres" # Name of the PostgreSQL container
DB_NAME="idp_data"               # Name of the database to backup
DB_USER="gemini"                 # PostgreSQL user
BACKUP_DIR="./backups"           # Directory to store backups
RETENTION_DAYS=7                 # Number of days to keep backups

# --- Functions ---

log_info() {
  echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_success() {
  echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
  echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" >&2
  exit 1
}

# --- Main Script Execution ---

log_info "Starting PostgreSQL database backup..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR" || log_error "Failed to create backup directory: $BACKUP_DIR"

# Generate timestamp for the backup file
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="$BACKUP_DIR/$DB_NAME-$TIMESTAMP.sql"

# Perform the backup using pg_dump from within the Docker container
log_info "Creating backup of database '$DB_NAME' to '$BACKUP_FILE'..."
docker exec "$DB_CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE" || log_error "PostgreSQL backup failed."

log_success "Database backup created successfully: $BACKUP_FILE"

# --- Cleanup Old Backups ---
log_info "Cleaning up old backups (retaining for $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -type f -name "$DB_NAME-*.sql" -mtime +"$RETENTION_DAYS" -delete || log_error "Failed to clean up old backups."
log_success "Old backups cleaned up."

log_success "Database backup process completed."

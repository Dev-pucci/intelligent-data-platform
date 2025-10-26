#!/bin/bash

# deployment.sh - Script to deploy the Intelligent Data Acquisition Platform on a VPS

# --- Configuration ---
REPO_URL="YOUR_GIT_REPOSITORY_URL" # e.g., https://github.com/youruser/intelligent-data-platform.git
PROJECT_DIR="intelligent-data-platform"
ENV_FILE=".env" # File to store environment variables

# --- Functions ---

log_info() {
  echo "[INFO] $1"
}

log_success() {
  echo "[SUCCESS] $1"
}

log_error() {
  echo "[ERROR] $1" >&2
  exit 1
}

# --- Pre-requisites ---

check_root() {
  if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root or with sudo."
  fi
}

install_docker() {
  if ! command -v docker &> /dev/null; then
    log_info "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh || log_error "Failed to download Docker installation script."
    sh get-docker.sh || log_error "Failed to install Docker."
    rm get-docker.sh
    log_success "Docker installed."
    # Add current user to docker group to run without sudo
    usermod -aG docker "$SUDO_USER" || log_error "Failed to add user to docker group."
    log_info "Please log out and log back in for Docker group changes to take effect for user $SUDO_USER."
  else
    log_info "Docker already installed."
  fi
}

install_docker_compose() {
  if ! command -v docker-compose &> /dev/null; then
    log_info "Docker Compose not found. Installing Docker Compose..."
    # Get the latest stable version of Docker Compose
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K[^"]*')
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose || log_error "Failed to download Docker Compose."
    chmod +x /usr/local/bin/docker-compose || log_error "Failed to set permissions for Docker Compose."
    log_success "Docker Compose installed."
  else
    log_info "Docker Compose already installed."
  fi
}

# --- Deployment Steps ---

clone_repo() {
  if [ -d "$PROJECT_DIR" ]; then
    log_info "Project directory '$PROJECT_DIR' already exists. Pulling latest changes..."
    cd "$PROJECT_DIR" || log_error "Failed to change directory to $PROJECT_DIR."
    git pull || log_error "Failed to pull latest changes."
    cd ..
  else
    log_info "Cloning repository '$REPO_URL'..."
    git clone "$REPO_URL" || log_error "Failed to clone repository."
  fi
}

setup_env_vars() {
  log_info "Setting up environment variables in '$PROJECT_DIR/$ENV_FILE'..."
  # Create .env file if it doesn't exist
  touch "$PROJECT_DIR/$ENV_FILE"

  # Example environment variables. User needs to fill these in.
  # Use sed to update or append.
  # DATABASE_URL="postgresql://gemini:password@postgres:5432/idp_data"
  # REDIS_URL="redis://redis:6379"
  # OLLAMA_API_KEY="YOUR_OLLAMA_API_KEY" # If needed for external access
  # OPENWEATHERMAP_API_KEY="YOUR_OPENWEATHERMAP_API_KEY" # For weather_api_json.yml example

  # Function to set or update an environment variable in the .env file
  set_env_var() {
    local key="$1"
    local value="$2"
    if grep -q "^${key}=" "$PROJECT_DIR/$ENV_FILE"; then
      sed -i "s|^${key}=.*|${key}=${value}|" "$PROJECT_DIR/$ENV_FILE"
    else
      echo "${key}=${value}" >> "$PROJECT_DIR/$ENV_FILE"
    fi
  }

  # Prompt user for sensitive variables
  read -p "Enter PostgreSQL password (default: password): " PG_PASSWORD
  PG_PASSWORD=${PG_PASSWORD:-password}
  set_env_var "POSTGRES_PASSWORD" "$PG_PASSWORD"
  set_env_var "DATABASE_URL" "postgresql://gemini:${PG_PASSWORD}@postgres:5432/idp_data"

  read -p "Enter API Base URL (default: http://localhost:8000): " API_BASE_URL
  API_BASE_URL=${API_BASE_URL:-http://localhost:8000}
  set_env_var "API_BASE_URL" "$API_BASE_URL"

  read -p "Enter CORS Allowed Origins (comma-separated, default: http://localhost,http://localhost:8080,http://localhost:3000): " CORS_ALLOWED_ORIGINS
  CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS:-http://localhost,http://localhost:8080,http://localhost:3000}
  set_env_var "CORS_ALLOWED_ORIGINS" "$CORS_ALLOWED_ORIGINS"

  read -p "Enter Gemini API Key (required for AI parsing): " GEMINI_API_KEY
  if [ -n "$GEMINI_API_KEY" ]; then
    set_env_var "GEMINI_API_KEY" "$GEMINI_API_KEY"
  else
    log_error "Gemini API Key is required for AI parsing. Please provide it."
  fi

  read -p "Enter OpenWeatherMap API Key (optional): " OWM_API_KEY
  if [ -n "$OWM_API_KEY" ]; then
    set_env_var "OPENWEATHERMAP_API_KEY" "$OWM_API_KEY"
  fi

  # Add other environment variables as needed
  log_success "Environment variables configured. Please review '$PROJECT_DIR/$ENV_FILE' for any additional configuration."}

deploy_services() {
  log_info "Building and starting Docker Compose services..."
  cd "$PROJECT_DIR" || log_error "Failed to change directory to $PROJECT_DIR."
  docker-compose build || log_error "Failed to build Docker Compose services."
  docker-compose up -d || log_error "Failed to start Docker Compose services."
  log_success "Docker Compose services deployed."
  cd ..
}

# --- Main Script Execution ---

check_root
install_docker
install_docker_compose
clone_repo
setup_env_vars
deploy_services

log_success "Deployment complete! Your services should now be running."
log_info "You can check the status with: cd $PROJECT_DIR && docker-compose ps"
log_info "Access Nginx at http://your_vps_ip"
log_info "Access Grafana at http://your_vps_ip/grafana (default user/pass: admin/admin)"
log_info "Access n8n at http://your_vps_ip/n8n"

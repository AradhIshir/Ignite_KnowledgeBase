#!/bin/bash
# Slack Knowledge Extractor - Installation Script
# This script sets up the complete Slack knowledge extraction system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/slack-knowledge-extractor"
SERVICE_USER="slack-extractor"
LOG_DIR="/var/log"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip3
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check cron
    if ! command -v crontab &> /dev/null; then
        print_error "cron is required but not installed"
        exit 1
    fi
    
    print_success "All system requirements met"
}

# Function to create service user
create_service_user() {
    print_status "Creating service user: $SERVICE_USER"
    
    if id "$SERVICE_USER" &>/dev/null; then
        print_warning "User $SERVICE_USER already exists"
    else
        useradd -r -s /bin/bash -d "$INSTALL_DIR" "$SERVICE_USER"
        print_success "Created service user: $SERVICE_USER"
    fi
}

# Function to create directories
create_directories() {
    print_status "Creating installation directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$LOG_DIR"
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    chmod 755 "$INSTALL_DIR"
    
    print_success "Created directories"
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Install required packages
    pip3 install requests python-dateutil
    
    print_success "Python dependencies installed"
}

# Function to copy files
copy_files() {
    print_status "Copying application files..."
    
    # Copy Python script
    cp slack_knowledge_extractor.py "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/slack_knowledge_extractor.py"
    
    # Copy wrapper script
    cp slack_extractor_wrapper.sh "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/slack_extractor_wrapper.sh"
    
    # Copy environment template
    cp env.example "$INSTALL_DIR/.env.example"
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    
    print_success "Application files copied"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f "$INSTALL_DIR/.env" ]; then
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
        chmod 600 "$INSTALL_DIR/.env"
        
        print_warning "Environment file created at $INSTALL_DIR/.env"
        print_warning "Please edit this file with your actual configuration values"
    else
        print_warning "Environment file already exists at $INSTALL_DIR/.env"
    fi
}

# Function to setup cron job
setup_cron() {
    print_status "Setting up cron job..."
    
    # Create cron job entry
    CRON_ENTRY="*/10 * * * * $INSTALL_DIR/slack_extractor_wrapper.sh >> $LOG_DIR/slack-extractor-cron.log 2>&1"
    
    # Add to root's crontab
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    
    print_success "Cron job installed (runs every 10 minutes)"
}

# Function to create systemd service (optional)
create_systemd_service() {
    print_status "Creating systemd service (optional)..."
    
    cat > /etc/systemd/system/slack-knowledge-extractor.service << EOF
[Unit]
Description=Slack Knowledge Extractor
After=network.target

[Service]
Type=oneshot
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/slack_extractor_wrapper.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    print_success "Systemd service created (optional - for manual runs)"
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    # Check if files exist
    if [ ! -f "$INSTALL_DIR/slack_knowledge_extractor.py" ]; then
        print_error "Python script not found"
        return 1
    fi
    
    if [ ! -f "$INSTALL_DIR/slack_extractor_wrapper.sh" ]; then
        print_error "Wrapper script not found"
        return 1
    fi
    
    if [ ! -f "$INSTALL_DIR/.env" ]; then
        print_error "Environment file not found"
        return 1
    fi
    
    # Test Python script syntax
    if ! python3 -m py_compile "$INSTALL_DIR/slack_knowledge_extractor.py"; then
        print_error "Python script has syntax errors"
        return 1
    fi
    
    print_success "Installation test passed"
    return 0
}

# Function to show next steps
show_next_steps() {
    echo
    print_success "Installation completed successfully!"
    echo
    print_status "Next steps:"
    echo "1. Edit the environment file: sudo nano $INSTALL_DIR/.env"
    echo "2. Add your Slack bot token and Supabase credentials"
    echo "3. Test the installation: sudo -u $SERVICE_USER $INSTALL_DIR/slack_extractor_wrapper.sh"
    echo "4. Check logs: tail -f $LOG_DIR/slack-knowledge-extractor.log"
    echo "5. Monitor cron execution: tail -f $LOG_DIR/slack-extractor-cron.log"
    echo
    print_status "Cron job is set to run every 10 minutes"
    print_status "Manual execution: sudo -u $SERVICE_USER $INSTALL_DIR/slack_extractor_wrapper.sh"
    echo
}

# Main installation function
main() {
    echo "=========================================="
    echo "Slack Knowledge Extractor Installation"
    echo "=========================================="
    echo
    
    check_root
    check_requirements
    create_service_user
    create_directories
    install_dependencies
    copy_files
    setup_environment
    setup_cron
    create_systemd_service
    
    if test_installation; then
        show_next_steps
    else
        print_error "Installation test failed"
        exit 1
    fi
}

# Run main function
main "$@"

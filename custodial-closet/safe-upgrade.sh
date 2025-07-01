#!/bin/bash

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info()    { echo -e "${BLUE}[INFO]${NC}    $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}    $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC}   $1"; }

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    log_error "This script must be run as root or with sudo."
    exit 1
fi

# Update
log_info "Running 'apt update'..."
if apt update; then
    log_success "Package lists updated successfully."
else
    log_error "'apt update' failed. Check your network or repositories."
    exit 1
fi

# Upgrade
log_info "Running 'apt upgrade'..."
if apt upgrade -y; then
    log_success "Packages upgraded successfully."
else
    log_error "'apt upgrade' failed. Check dependencies or disk space."
    exit 1
fi

# Autoclean
log_info "Running 'apt autoclean'..."
if apt autoclean; then
    log_success "Obsolete .deb files removed."
else
    log_warn "'apt autoclean' completed with warnings (or nothing to clean)."
fi

# Dry-run autoremove
log_info "Checking what 'apt autoremove' would remove (dry run)..."
REMOVABLE_PACKAGES=$(apt autoremove --dry-run 2>&1 | grep -Po '^Remv \K[^ ]+')

if [ -z "$REMOVABLE_PACKAGES" ]; then
    log_success "No packages to autoremove."
    exit 0
else
    log_warn "The following packages will be removed:"
    echo -e "${YELLOW}$REMOVABLE_PACKAGES${NC}"
fi

# Confirmation prompt
read -p "$(echo -e "${BLUE}[ACTION]${NC}   Proceed with 'apt autoremove -y'? [y/N] ")" -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Running 'apt autoremove -y'..."
    if apt autoremove -y; then
        log_success "Unused packages removed successfully."
    else
        log_error "'apt autoremove' failed. Check logs."
    fi
else
    log_info "Autoremove canceled by user."
fi


#!/usr/bin/bash
#
# Copr Build Script for Bazzite Gaming Optimizer
# Builds RPM packages for Fedora and Bazzite Linux
#

set -e

PROJECT_NAME="bazzite-optimizer"
COPR_REPO="doublegate/bazzite-optimizer"
VERSION="1.1.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if copr-cli is installed
if ! command -v copr-cli &> /dev/null; then
    print_error "copr-cli is not installed"
    print_info "Install with: sudo dnf install copr-cli"
    exit 1
fi

# Check if authenticated
if ! copr-cli whoami &> /dev/null; then
    print_error "Not authenticated with Copr"
    print_info "Run: copr-cli login"
    exit 1
fi

# Create source tarball
print_info "Creating source tarball..."
cd "$(dirname "$0")/../.."
git archive --format=tar.gz --prefix="${PROJECT_NAME}-${VERSION}/" \
    -o "${PROJECT_NAME}-${VERSION}.tar.gz" HEAD

# Build SRPM
print_info "Building SRPM..."
rpmbuild -bs packaging/rpm/${PROJECT_NAME}.spec \
    --define "_sourcedir $(pwd)" \
    --define "_srcrpmdir $(pwd)"

SRPM="${PROJECT_NAME}-${VERSION}-1.*.src.rpm"

# Submit build to Copr
print_info "Submitting build to Copr: ${COPR_REPO}"
copr-cli build "${COPR_REPO}" "${SRPM}"

print_info "Build submitted successfully!"
print_info "Monitor progress at: https://copr.fedorainfracloud.org/coprs/${COPR_REPO}/builds/"

# Cleanup
rm -f "${PROJECT_NAME}-${VERSION}.tar.gz" "${SRPM}"

print_info "Done!"

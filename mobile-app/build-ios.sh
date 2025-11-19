#!/bin/bash
# Bazzite Gaming Optimizer - Mobile App iOS Build Script
# Builds production iOS IPA for deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Bazzite Gaming Optimizer - iOS Build${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: iOS builds can only be performed on macOS${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: package.json not found. Please run from mobile-app directory.${NC}"
    exit 1
fi

# Check for required tools
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v node >/dev/null 2>&1 || { echo -e "${RED}Error: Node.js is not installed${NC}"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}Error: npm is not installed${NC}"; exit 1; }
command -v pod >/dev/null 2>&1 || { echo -e "${RED}Error: CocoaPods is not installed. Run: sudo gem install cocoapods${NC}"; exit 1; }
command -v xcodebuild >/dev/null 2>&1 || { echo -e "${RED}Error: Xcode is not installed${NC}"; exit 1; }

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
npm install

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${RED}Error: Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}Dependencies installed successfully${NC}"

# Install CocoaPods dependencies
echo -e "\n${YELLOW}Installing CocoaPods dependencies...${NC}"
cd ios
pod install
cd ..
echo -e "${GREEN}CocoaPods dependencies installed${NC}"

# Build type selection
BUILD_TYPE=${1:-debug}
SCHEME="BazziteOptimizer"  # Update with your actual scheme name

if [ "$BUILD_TYPE" = "release" ]; then
    echo -e "\n${YELLOW}Building production IPA...${NC}"
    echo -e "${YELLOW}Note: This requires proper code signing configuration${NC}"

    cd ios
    xcodebuild clean archive \
        -workspace BazziteOptimizer.xcworkspace \
        -scheme "$SCHEME" \
        -configuration Release \
        -archivePath build/BazziteOptimizer.xcarchive \
        CODE_SIGN_IDENTITY="" \
        CODE_SIGNING_REQUIRED=NO \
        CODE_SIGNING_ALLOWED=NO

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}Archive Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Archive:${NC} ios/build/BazziteOptimizer.xcarchive"
    echo -e "${YELLOW}Note: Use Xcode to export IPA with proper signing${NC}"

else
    echo -e "\n${YELLOW}Building debug version...${NC}"
    echo -e "${YELLOW}Use Xcode to build and run on simulator/device${NC}"

    cd ios
    xcodebuild clean build \
        -workspace BazziteOptimizer.xcworkspace \
        -scheme "$SCHEME" \
        -configuration Debug \
        -sdk iphonesimulator \
        -destination 'platform=iOS Simulator,name=iPhone 14'

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}Build Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${YELLOW}Launch iOS Simulator and install the app from Xcode${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Build process completed!${NC}"
echo -e "${BLUE}========================================${NC}"

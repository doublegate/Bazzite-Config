#!/bin/bash
# Bazzite Gaming Optimizer - Mobile App Android Build Script
# Builds production Android APK/AAB for deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Bazzite Gaming Optimizer - Android Build${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: package.json not found. Please run from mobile-app directory.${NC}"
    exit 1
fi

# Check for required tools
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v node >/dev/null 2>&1 || { echo -e "${RED}Error: Node.js is not installed${NC}"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}Error: npm is not installed${NC}"; exit 1; }

# Check for Android SDK
if [ -z "$ANDROID_HOME" ]; then
    echo -e "${RED}Error: ANDROID_HOME environment variable not set${NC}"
    echo -e "${YELLOW}Please install Android SDK and set ANDROID_HOME${NC}"
    exit 1
fi

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
npm install

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${RED}Error: Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}Dependencies installed successfully${NC}"

# Build type selection
BUILD_TYPE=${1:-debug}

if [ "$BUILD_TYPE" = "release" ]; then
    echo -e "\n${YELLOW}Building production APK...${NC}"
    cd android
    ./gradlew clean
    ./gradlew assembleRelease

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}Build Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Production APK:${NC} android/app/build/outputs/apk/release/app-release.apk"
    echo -e "${YELLOW}Note: APK needs to be signed before distribution${NC}"

elif [ "$BUILD_TYPE" = "bundle" ]; then
    echo -e "\n${YELLOW}Building Android App Bundle (AAB)...${NC}"
    cd android
    ./gradlew clean
    ./gradlew bundleRelease

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}Build Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Production AAB:${NC} android/app/build/outputs/bundle/release/app-release.aab"
    echo -e "${YELLOW}Note: AAB needs to be signed before uploading to Play Store${NC}"

else
    echo -e "\n${YELLOW}Building debug APK...${NC}"
    cd android
    ./gradlew clean
    ./gradlew assembleDebug

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}Build Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Debug APK:${NC} android/app/build/outputs/apk/debug/app-debug.apk"
    echo -e "${YELLOW}Installing to connected device...${NC}"
    adb install -r app/build/outputs/apk/debug/app-debug.apk || echo -e "${YELLOW}No device connected, skipping install${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Build process completed!${NC}"
echo -e "${BLUE}========================================${NC}"

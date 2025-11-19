# Bazzite Gaming Optimizer - Mobile Deployment Guide

Complete guide for building, testing, and deploying the React Native mobile companion app for Android and iOS platforms.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Backend WebSocket Server](#backend-websocket-server)
- [Android Deployment](#android-deployment)
- [iOS Deployment](#ios-deployment)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Distribution](#distribution)

---

## Overview

The Bazzite Gaming Optimizer mobile companion app is a React Native application that provides:

- **Real-Time Monitoring**: Live CPU, GPU, RAM, power, and temperature metrics
- **Profile Management**: Apply gaming profiles remotely
- **Alerts & Notifications**: System alerts and performance warnings
- **QR Code Pairing**: Secure device authentication with the backend server

**Technology Stack**:
- **Framework**: React Native 0.72
- **UI Library**: React Native Paper (Material Design)
- **Navigation**: React Navigation 6.x
- **Real-Time Communication**: WebSocket (ws library)
- **Charts**: React Native Chart Kit

---

## Prerequisites

### All Platforms

- **Node.js**: 16.x or higher
- **npm**: 8.x or higher (or yarn 1.22+)
- **Git**: For cloning the repository

```bash
# Verify installations
node --version  # Should be v16.x or higher
npm --version   # Should be v8.x or higher
```

### Android Development

- **Java Development Kit (JDK)**: 11 or higher
- **Android Studio**: Latest stable version
- **Android SDK**: API Level 31 (Android 12) minimum
- **Android SDK Build Tools**: 31.0.0+
- **Android Emulator** (optional, for testing)

**Environment Variables**:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### iOS Development (macOS only)

- **macOS**: 11.0 (Big Sur) or higher
- **Xcode**: 13.0 or higher
- **CocoaPods**: 1.11+ (`sudo gem install cocoapods`)
- **Xcode Command Line Tools**: `xcode-select --install`
- **iOS Simulator** or physical device for testing

---

## Development Setup

### 1. Install Dependencies

Navigate to the mobile-app directory:

```bash
cd mobile-app
npm install
```

### 2. iOS Additional Setup (macOS only)

Install CocoaPods dependencies:

```bash
cd ios
pod install
cd ..
```

### 3. Configuration

Create a configuration file for the WebSocket server connection:

```typescript
// mobile-app/src/config/server.ts
export const SERVER_CONFIG = {
  // Replace with your server's IP address
  host: '192.168.1.100',  // Your Bazzite machine IP
  port: 8081,

  // For local development
  // host: 'localhost',
  // port: 8081,
};
```

**Finding Your Server IP**:

```bash
# On your Bazzite machine
ip addr show | grep "inet " | grep -v 127.0.0.1
```

### 4. Start Metro Bundler

```bash
npm start
```

Keep this terminal open. Metro Bundler serves the JavaScript bundle to your app.

---

## Backend WebSocket Server

### Starting the Server

On your Bazzite gaming machine, start the WebSocket server:

```bash
cd /path/to/Bazzite-Config
python3 mobile_api/websocket_server.py
```

The server will start on port 8081 by default.

**Server Features**:
- QR code generation for device pairing
- Real-time metrics broadcasting every 2 seconds
- Automatic device reconnection handling
- Support for multiple connected devices

**Server Output**:
```
🚀 Starting Bazzite Gaming Optimizer WebSocket Server...
📱 Server URL: ws://192.168.1.100:8081
🔐 Pairing enabled - scan QR code from mobile app

QR Code for Pairing:
█████████████████████████
█ ▄▄▄▄▄ █ ▀█▄█ ▄▄▄▄▄ █
█ █   █ █▄▀▄  █ █   █ █
...
```

### Firewall Configuration

Allow WebSocket connections through the firewall:

```bash
# Fedora/Bazzite
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --reload

# Ubuntu/Debian
sudo ufw allow 8081/tcp
```

---

## Android Deployment

### Development Build (Debug)

**Using Build Script**:
```bash
./build-android.sh debug
```

**Manual Build**:
```bash
cd android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### Production Build (Release)

**1. Generate Signing Key**:

```bash
keytool -genkeypair -v -storetype PKCS12 \
  -keystore bazzite-optimizer-release.keystore \
  -alias bazzite-optimizer \
  -keyalg RSA -keysize 2048 -validity 10000
```

**2. Configure Signing** (`android/gradle.properties`):

```properties
BAZZITE_OPTIMIZER_UPLOAD_STORE_FILE=bazzite-optimizer-release.keystore
BAZZITE_OPTIMIZER_UPLOAD_KEY_ALIAS=bazzite-optimizer
BAZZITE_OPTIMIZER_UPLOAD_STORE_PASSWORD=your_store_password
BAZZITE_OPTIMIZER_UPLOAD_KEY_PASSWORD=your_key_password
```

**3. Update `android/app/build.gradle`**:

```gradle
android {
    ...
    signingConfigs {
        release {
            if (project.hasProperty('BAZZITE_OPTIMIZER_UPLOAD_STORE_FILE')) {
                storeFile file(BAZZITE_OPTIMIZER_UPLOAD_STORE_FILE)
                storePassword BAZZITE_OPTIMIZER_UPLOAD_STORE_PASSWORD
                keyAlias BAZZITE_OPTIMIZER_UPLOAD_KEY_ALIAS
                keyPassword BAZZITE_OPTIMIZER_UPLOAD_KEY_PASSWORD
            }
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro"
        }
    }
}
```

**4. Build Release APK**:

```bash
./build-android.sh release
```

Output: `android/app/build/outputs/apk/release/app-release.apk`

**5. Build App Bundle (for Google Play)**:

```bash
./build-android.sh bundle
```

Output: `android/app/build/outputs/bundle/release/app-release.aab`

### Installing on Device

**Via ADB**:
```bash
adb devices  # Verify device connected
adb install -r android/app/build/outputs/apk/release/app-release.apk
```

**Manual Installation**:
1. Transfer APK to device
2. Enable "Install from Unknown Sources" in Settings
3. Open APK file to install

---

## iOS Deployment

### Development Build (Debug)

**1. Open Xcode Project**:

```bash
open ios/BazziteOptimizer.xcworkspace
```

**2. Select Simulator**:
- Click on the device selector in Xcode toolbar
- Choose iPhone 14 (or your preferred simulator)

**3. Build and Run**:
- Press ⌘R or click the Play button
- App will build and launch in simulator

**Using Build Script**:
```bash
./build-ios.sh debug
```

### Production Build (Release)

**1. Configure Code Signing**:

- Open `ios/BazziteOptimizer.xcworkspace` in Xcode
- Select the BazziteOptimizer target
- Go to "Signing & Capabilities" tab
- Select your development team
- Choose an automatic or manual signing certificate

**2. Configure App Information** (`ios/BazziteOptimizer/Info.plist`):

```xml
<key>CFBundleDisplayName</key>
<string>Bazzite Optimizer</string>
<key>CFBundleIdentifier</key>
<string>com.yourcompany.bazziteoptimizer</string>
<key>CFBundleVersion</key>
<string>1</string>
<key>CFBundleShortVersionString</key>
<string>1.6.0</string>
```

**3. Build Archive**:

```bash
./build-ios.sh release
```

Or in Xcode:
- Product → Archive
- Wait for archive to complete
- Xcode Organizer opens automatically

**4. Export IPA**:

In Xcode Organizer:
- Select the archive
- Click "Distribute App"
- Choose distribution method:
  - **Development**: For testing on registered devices
  - **Ad Hoc**: For testing outside App Store
  - **App Store**: For App Store submission
- Follow the wizard to export IPA

### Installing on Device

**Development/Ad Hoc Builds**:

1. Connect device to Mac
2. Drag IPA to Xcode Devices window
3. Or use TestFlight for distribution

**App Store Build**:

1. Upload to App Store Connect via Xcode
2. Configure app metadata in App Store Connect
3. Submit for review

---

## Testing

### Unit Testing

```bash
npm test
```

### Integration Testing

**Start Test Environment**:

```bash
# Terminal 1: Start WebSocket server
python3 mobile_api/websocket_server.py

# Terminal 2: Start Metro Bundler
cd mobile-app
npm start

# Terminal 3: Run tests
npm run test:integration
```

### End-to-End Testing

**Manual Testing Checklist**:

- [ ] QR code pairing with backend server
- [ ] Real-time metrics display (CPU, GPU, RAM, power)
- [ ] Profile switching (Competitive, Balanced, Streaming)
- [ ] Alert notifications for high temperatures
- [ ] Reconnection after network interruption
- [ ] Settings persistence across app restarts
- [ ] Dark theme consistency

### Performance Testing

**React Native Performance Monitor**:

In development mode, shake device and enable "Show Perf Monitor"

**Key Metrics**:
- **FPS**: Should maintain 60 FPS during normal operation
- **Memory**: Monitor for memory leaks during extended use
- **Network**: WebSocket connection stability over time

---

## Troubleshooting

### Android Issues

**Gradle Build Fails**:
```bash
cd android
./gradlew clean
rm -rf .gradle
./gradlew assembleDebug
```

**ADB Not Detecting Device**:
```bash
adb kill-server
adb start-server
adb devices
```

**Metro Bundler Connection Error**:
```bash
adb reverse tcp:8081 tcp:8081
```

### iOS Issues

**CocoaPods Installation Fails**:
```bash
cd ios
pod deintegrate
pod install --repo-update
```

**Xcode Build Fails**:
- Clean build folder: Product → Clean Build Folder (⌘⇧K)
- Delete derived data: `rm -rf ~/Library/Developer/Xcode/DerivedData`
- Restart Xcode

**Simulator Not Launching**:
```bash
xcrun simctl erase all
open -a Simulator
```

### WebSocket Connection Issues

**Cannot Connect to Server**:

1. Verify server is running: `curl http://YOUR_IP:8081/health`
2. Check firewall settings
3. Verify IP address in `server.ts` configuration
4. Ensure mobile device is on same network as server

**Connection Drops Frequently**:

1. Check network stability
2. Increase reconnection timeout in WebSocketService
3. Verify server logs for errors

---

## Distribution

### Android Distribution

**Google Play Store**:

1. Create developer account ($25 one-time fee)
2. Build signed AAB: `./build-android.sh bundle`
3. Upload to Google Play Console
4. Complete store listing (screenshots, description, icon)
5. Submit for review

**Alternative Distribution**:
- **F-Droid**: Open-source app store
- **Direct APK**: Host on website for manual download
- **Enterprise**: Internal distribution via MDM

### iOS Distribution

**App Store**:

1. Enroll in Apple Developer Program ($99/year)
2. Create app in App Store Connect
3. Build and upload via Xcode
4. Complete app metadata
5. Submit for review (typically 1-2 days)

**Alternative Distribution**:
- **TestFlight**: Beta testing (100 internal, 10,000 external testers)
- **Enterprise**: Apple Developer Enterprise Program
- **Ad Hoc**: Limited to 100 devices per year

---

## Security Best Practices

### Authentication

- Implement token-based authentication for WebSocket connections
- Use HTTPS/WSS in production (TLS/SSL certificates)
- Rotate pairing tokens regularly (current: 300s expiry)
- Implement rate limiting on server

### Data Privacy

- Do not log sensitive system information
- Encrypt WebSocket communication in production
- Clear authentication tokens on logout
- Implement certificate pinning for production builds

### Code Obfuscation

**Android (ProGuard)**:
Already enabled in release builds via `build.gradle`

**iOS**:
Configure in Xcode Build Settings:
- Strip Debug Symbols: Yes
- Enable Bitcode: Yes
- Optimization Level: Fastest, Smallest [-Os]

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Mobile CI

on: [push, pull_request]

jobs:
  android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 16
      - name: Install dependencies
        working-directory: mobile-app
        run: npm install
      - name: Build Android
        working-directory: mobile-app/android
        run: ./gradlew assembleDebug

  ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 16
      - name: Install dependencies
        working-directory: mobile-app
        run: npm install
      - name: Install CocoaPods
        working-directory: mobile-app/ios
        run: pod install
      - name: Build iOS
        working-directory: mobile-app/ios
        run: xcodebuild -workspace BazziteOptimizer.xcworkspace -scheme BazziteOptimizer -sdk iphonesimulator -configuration Debug
```

---

## Additional Resources

**React Native Documentation**: https://reactnative.dev/docs/getting-started
**React Navigation**: https://reactnavigation.org/docs/getting-started
**React Native Paper**: https://callstack.github.io/react-native-paper/
**Android Developer Guide**: https://developer.android.com/
**iOS Developer Guide**: https://developer.apple.com/

**Support**: Open an issue on GitHub for deployment assistance

---

**Version**: 1.6.0
**Last Updated**: November 19, 2025
**Author**: Bazzite Gaming Optimizer Team

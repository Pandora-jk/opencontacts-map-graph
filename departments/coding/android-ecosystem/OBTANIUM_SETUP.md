# Obtanium Auto-Update Setup Guide

## Overview
This document outlines the steps to make the Android Contacts App installable and updatable via Obtanium.

## What is Obtanium?
Obtainium is an Android app that allows you to install and update apps directly from their source (GitHub Releases, GitLab, F-Droid, etc.) without needing Google Play Store or F-Droid.

## Requirements for Obtanium Support

### 1. GitHub Releases
- **Must have**: GitHub repository with Releases
- **APK assets**: Each release must include signed APK files
- **Version tags**: Semantic versioning (e.g., v1.0.0, v1.2.3)
- **Release notes**: Changelog for each version

### 2. APK Signing
- **Consistent signing**: All APKs must be signed with the same key
- **Release builds**: Use release-signed APKs (not debug builds)
- **Key management**: Store signing keys securely (Bitwarden)

### 3. Version Management
- **Semantic versioning**: MAJOR.MINOR.PATCH (e.g., 1.0.0)
- **Version code**: Incrementing integer in build.gradle.kts
- **Version name**: Human-readable version string

## Current Status

### ✅ Completed
- [x] Android project structure created
- [x] Material You dynamic colors implemented
- [x] APK builds successfully (debug version)
- [x] GitHub repository initialized

### ⏳ In Progress
- [ ] Create GitHub Releases with APK assets
- [ ] Setup release signing configuration
- [ ] Configure CI/CD for automated builds
- [ ] Document Obtanium installation URL

### ❌ Pending
- [ ] Release signing key generation and storage
- [ ] First stable release (v1.0.0)
- [ ] Automated build workflow (GitHub Actions)
- [ ] Release notes template

## Implementation Steps

### Step 1: Generate Release Signing Key
```bash
keytool -genkey -v -keystore contacts-app.keystore -alias contacts-app -keyalg RSA -keysize 2048 -validity 10000
```
**Action**: Store keystore password and credentials in Bitwarden under "Android Contacts App Keystore"

### Step 2: Configure Gradle for Release Builds
Add to `contacts-app/build.gradle.kts`:
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("../keystore/contacts-app.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = "contacts-app"
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }
    
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

### Step 3: Create First GitHub Release (v1.0.0)
**Version**: 1.0.0
**Tag**: v1.0.0
**Title**: Initial Release - Material You Support
**Content**:
```
## Features
- Material You dynamic colors (Android 12+)
- System theme integration (light/dark auto-switch)
- Full contact CRUD operations
- 4-tab interface (All, Favorites, Groups, Map)
- Search functionality
- Quick actions (call, message, email)
- Favorites management
- Groups integration

## Technical Details
- Min SDK: Android 8.0 (API 26)
- Target SDK: Android 14 (API 34)
- Architecture: MVVM with Kotlin
- Database: Room

## Installation
1. Download contacts-app-release.apk
2. Install on Android device
3. Add to Obtanium: https://github.com/YOUR_USERNAME/android-ecosystem

## Known Issues
- Test compilation errors (being fixed)
- Unit tests need updates
```

### Step 4: Setup GitHub Actions for CI/CD
Create `.github/workflows/android-release.yml`:
```yaml
name: Android Release Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Build release APK
        run: ./gradlew :contacts-app:assembleRelease
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: contacts-app/build/outputs/apk/release/contacts-app-release.apk
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 5: Document Obtanium Installation
**Installation URL for Obtanium**:
```
https://github.com/YOUR_USERNAME/android-ecosystem
```

**Configuration**:
- Source Type: GitHub
- Repository: `YOUR_USERNAME/android-ecosystem`
- Asset filter: `contacts-app-release.apk`
- Version sorting: Semantic

## Testing Obtanium Integration

1. **Install Obtanium** on Android device
2. **Add app source**:
   - Open Obtanium
   - Tap "+" to add new app
   - Enter GitHub URL: `https://github.com/YOUR_USERNAME/android-ecosystem`
   - Configure filters if needed
3. **Install**: Tap install on the detected APK
4. **Verify updates**: Push new release and check Obtanium notification

## Next Actions

### Immediate (Today)
1. ✅ Create GitHub repository (if not exists)
2. ✅ Generate release signing key
3. ✅ Store credentials in Bitwarden
4. ⏳ Build first release APK (signed)
5. ⏳ Create v1.0.0 tag and release
6. ⏳ Upload APK to release

### Short-term (This Week)
- [ ] Setup GitHub Actions CI/CD
- [ ] Test Obtanium installation flow
- [ ] Document in README.md
- [ ] Add release notes template

### Long-term
- [ ] Automated builds on every tag
- [ ] Beta channel support
- [ ] Multiple APK variants (arm64, universal)

## References
- [Obtainium GitHub](https://github.com/ImranR98/Obtainium)
- [Obtainium Website](https://obtainium.imranr.dev/)
- [Obtainium Wiki](https://wiki.obtainium.imranr.dev/)
- [GitHub Releases Documentation](https://docs.github.com/en/releases)
- [Android App Signing](https://developer.android.com/studio/publish/app-signing)

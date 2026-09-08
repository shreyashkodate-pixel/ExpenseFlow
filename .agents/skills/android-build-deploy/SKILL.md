---
name: android-build-deploy
description: Build, test, and deploy the ExpenseFlow Android Native application using headless CLI tools and ADB without Android Studio.
---

# Android Build & Deploy Runbook

This skill outlines the headless command-line workflow for building, testing, and deploying the ExpenseFlow Android Native app.

## Environment Setup
```bash
export ANDROID_HOME=~/Library/Android/sdk
export PATH=$ANDROID_HOME/platform-tools:$PATH
```

## Compilation & Unit Testing
Navigate to `ExpenseFlow/android`:

1. **Run Unit Tests**:
   ```bash
   ./gradlew testDebugUnitTest
   ```

2. **Assemble Debug APK**:
   ```bash
   ./gradlew assembleDebug
   ```
   *Note: If modifying Hilt ViewModels, always clean first:*
   ```bash
   ./gradlew clean assembleDebug
   ```

## USB Device Deployment
1. Verify device connection:
   ```bash
   adb devices
   ```
2. Stream install the compiled APK:
   ```bash
   adb install -r app/build/outputs/apk/debug/app-debug.apk
   ```
3. Launch the app on device:
   ```bash
   adb shell am start -n com.expenseflow.app/.MainActivity
   ```

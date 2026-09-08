# ExpenseFlow Android Native Application

A high-performance Android Native mobile application built with **Kotlin** and **Jetpack Compose**, connecting to the ExpenseFlow FastAPI backend and PostgreSQL database.

Built and maintained entirely through **headless command-line tools and Gradle**, without requiring Android Studio.

---

## 📱 Features

1. **Dark Glassmorphism Design System**:
   - Slate dark backdrop (`#090D16`), translucent card surfaces (`#111827`), glowing violet accents (`#8B5CF6`), and semantic status colors.
   - Reusable primitives: `GlassCard`, `PrimaryButton`, `ExpenseInputField`, `StatusBadge`, `LoadingIndicator`.

2. **Hardware-Backed Security & Auth Flow**:
   - Hardware Keystore storage using `EncryptedSharedPreferences` with AES-256-GCM.
   - Dual-token lifecycle: Short-lived access tokens + long-lived refresh tokens.
   - Silent 401 token refresh via OkHttp `Authenticator` with automatic request replay.
   - 4-step OTP registration wizard with 6 individual digit boxes and 60-second cooldown.

3. **Offline-First Expense Management**:
   - Local persistence via SQLite Room (`ExpenseEntity`, `CategoryEntity`, `ExpenseDao`, `CategoryDao`).
   - Seamless background synchronization with cloud PostgreSQL.
   - Real-time search, category filtering, and payment method tagging (`UPI`, `GPay`, `Cash`, `Card`, `Transfer`).
   - PDF and CSV report exports streamed directly to the device *Downloads* folder.

4. **Budgets & Pacing Radar**:
   - Real-time budget pacing progress indicator with status badges (`OK`, `WARNING`, `EXCEEDED`).
   - Category-specific spending limit configuration.

5. **Analytics & Spending Trends**:
   - Interactive daily spending trend bar charts.
   - Category distribution percentage breakdown with total spend aggregates.

6. **Full AI Financial Intelligence Suite**:
   - **Financial Health Score**: Dynamic 0–100 rating with contextual headline.
   - **Spending Spike Detection**: Identifies unusual surges (e.g. +35% Dining Out).
   - **Predictive Pacing Alerts**: Daily burn rate (₹/day), safe daily ceiling, and forecasted exhaustion date.
   - **Subscription Audit**: 90-day recurring merchant audit with monthly commitment overhead.
   - **50/30/20 Wealth Allocation**: Segmented meter for Needs (50%), Wants (30%), and Savings (20%) with rebalancing advice.
   - **Interactive AI Assistant**: Slide-up conversational drawer powered by Gemini RAG, grounded in live database records, with data pills and follow-up prompt chips.

---

## 🛠 Tech Stack

- **Language**: Kotlin 2.0.20
- **UI Framework**: Jetpack Compose (BOM 2024.06.00) + Material 3
- **Dependency Injection**: Google Hilt 2.51.1 (`@HiltAndroidApp`, `@HiltViewModel`)
- **Networking**: Retrofit 2.11.0 + OkHttp 4.12.0 + Kotlinx Serialization
- **Local Database**: Room 2.6.1 SQLite
- **Security**: Android Jetpack Security (`androidx.security:security-crypto:1.1.0-alpha06`)
- **Build System**: Gradle 8.9 + Android Gradle Plugin 8.5.2

---

## 🚀 Building via Command Line (Zero Android Studio)

### Prerequisites
- JDK 17 or higher (`java -version`)
- Android SDK (`platforms;android-34`, `build-tools;34.0.0`)
- Android platform-tools (`adb`)

Ensure your environment variables are set:
```bash
export ANDROID_HOME=~/Library/Android/sdk
export PATH=$ANDROID_HOME/platform-tools:$PATH
```

### Build APK
Navigate to the `android/` directory:
```bash
cd android
./gradlew assembleDebug
```
The compiled APK will be located at:
`android/app/build/outputs/apk/debug/app-debug.apk`

### Run Unit Tests
```bash
./gradlew testDebugUnitTest
```

### Clean Project
```bash
./gradlew clean
```

---

## 📲 Installing & Running on a Physical Device

1. Connect your Android device via USB.
2. Enable **Developer Options** on your phone (Tap *Build Number* 7 times in Settings > About Phone).
3. Enable **USB Debugging** in *Developer Options*.
4. Verify the device is recognized:
   ```bash
   adb devices
   ```
5. Install and launch the application:
   ```bash
   # Stream install the debug APK
   adb install -r app/build/outputs/apk/debug/app-debug.apk

   # Launch the MainActivity
   adb shell am start -n com.expenseflow.app/.MainActivity
   ```

---

## 🌐 Dynamic Backend URL Configuration

The application uses `BuildConfig.BASE_URL` which defaults to the cloud production backend:
`https://expenseflow-sle3.onrender.com/api/v1/`

To point to a local development backend or custom server during build:
```bash
EXPENSEFLOW_API_URL="http://10.0.2.2:8000/api/v1/" ./gradlew assembleDebug
```
*(Note: Use `10.0.2.2` for Android Emulator localhost, or your computer's LAN IP e.g. `http://192.168.1.X:8000/api/v1/` for physical devices on the same Wi-Fi network).*

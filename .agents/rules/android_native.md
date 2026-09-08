# Android Native Application Rules & Repository Memory

This document records the architectural standards, command-line protocols, and development memory for the Android Native application in `android/`.

---

## 1. Dual-Client Architecture & Zero Android Studio Rule
- **Dual-Client Preservation**: The native Android application resides exclusively in `android/`. Never modify or break the Next.js web client in `frontend/` or the FastAPI backend in `backend/` when making Android updates.
- **Headless CLI Development**: All compilation, packaging, and device deployment must be executable strictly via terminal / Antigravity commands without requiring the Android Studio IDE:
  - SDK Path: `export ANDROID_HOME=~/Library/Android/sdk && export PATH=$ANDROID_HOME/platform-tools:$PATH`
  - Build: `./gradlew assembleDebug`
  - Tests: `./gradlew testDebugUnitTest`
  - Clean: `./gradlew clean assembleDebug`

---

## 2. Dependency Injection & Hilt Gotcha
- **Hilt ASM Incremental Bytecode**:
  - When introducing or altering `@HiltViewModel` classes or `@InstallIn` modules, incremental dexing may fail with duplicate class errors in `transformDebugClassesWithAsm`.
  - **Resolution**: Always execute `./gradlew clean assembleDebug` when altering Hilt-annotated classes.

---

## 3. Serialization & DTO Standards
- **Naming Conventions**:
  - Backend FastAPI JSON schemas utilize `snake_case`.
  - Kotlin data classes MUST use `camelCase` with explicit `@SerialName("snake_case")` annotations.
  - Never access or declare snake_case properties directly in Kotlin models.
  - JSON parser configuration in `NetworkModule.kt` enforces: `ignoreUnknownKeys = true`, `coerceInputValues = true`, `isLenient = true`, `encodeDefaults = true`.

---

## 4. Jetpack Compose UI & Glassmorphism Guidelines
- **Zero Inline Styling**: All colors and styles must reference the design system in `ui/theme/`:
  - `BackgroundDark` (`#090D16`), `SurfaceDark` (`#111827`), `PrimaryViolet` (`#8B5CF6`)
  - `AccentEmerald` (`#10B981`), `WarningAmber` (`#F59E0B`), `ErrorRose` (`#F43F5E`)
- **Iteration in Composables**:
  - Never call `@Composable` functions inside standard `.forEach { ... }` lambdas.
  - Always use a standard `for (item in items) { ... }` loop or `items(items) { ... }` in a `LazyColumn` / `LazyRow`.
- **Top-Level Navigation**:
  - Main app uses 4 primary navigation tabs: `Home`, `Expenses`, `Budgets`, `Analytics`.
  - AI Assistant drawer is globally accessible via `AIChatBottomSheet` and the floating action button.

---

## 5. Security & Keystore
- **Tokens**:
  - Access and refresh tokens are stored in hardware-backed Keystore storage via `EncryptedSharedPreferences` (`SessionManager.kt`) using AES-256-GCM.
  - Network requests automatically attach Bearer token via `AuthInterceptor`.
  - 401 Unauthorized responses trigger automatic silent token refresh and replay via `TokenAuthenticator`.
- **Environment Variables**:
  - API base URL is configured via Gradle `BuildConfig.BASE_URL`:
    - Defaults to: `https://expenseflow-sle3.onrender.com/api/v1/`
    - Debug override via environment variable `EXPENSEFLOW_API_URL`.

---

## 6. Offline-First SQLite Room Persistence
- All user expenses and categories are cached locally in `ExpenseFlowDatabase` (`ExpenseEntity`, `CategoryEntity`).
- Mutations first execute locally and sync to the cloud PostgreSQL database.
- Reports (PDF / CSV) are streamed directly to the device *Downloads* folder via Android `DownloadManager`.

---

## 7. Device Testing via USB ADB
- Check attached device: `adb devices`
- Stream install APK: `adb install -r android/app/build/outputs/apk/debug/app-debug.apk`
- Bring MainActivity to front: `adb shell am start -n com.expenseflow.app/.MainActivity`

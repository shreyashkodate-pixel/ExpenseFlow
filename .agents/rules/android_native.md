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

## 4. Jetpack Compose UI & Stitch Design System Guidelines
- **Zero Inline Styling**: All colors and styles must reference the design system in `ui/theme/`:
  - **Stitch Core Tokens**:
    - `CanvasLight` (`#F8F9FF`), `SurfaceContainerLow` (`#F1F4FA`), `CardBorderLight` (`#E2E8F0`)
    - `BrandNavy` (`#0A1128`), `BrandNavyDark` (`#030712`), `PrimaryContainer` (`#131B2E`)
    - `BrandIceBlue` (`#93C5FD`), `BrandEmerald` (`#006C49`), `IncomeBadge` (`#E6F4EA`)
    - `WarningAmber` (`#F59E0B`), `ErrorRose` (`#F43F5E`)
  - **Dark Mode Semantics**: Use dynamic `MaterialTheme.colorScheme.surfaceVariant` or luminance-aware branching (`MaterialTheme.colorScheme.surface.luminance() < 0.5f`) to prevent low-contrast text on surfaces. Avoid hardcoded `SurfaceContainerLow` on dark mode backgrounds.
- **Compose Layout in Bar Charts**:
  - When `.fillMaxHeight(fraction)` is applied to an element inside a `Column` that also has `.fillMaxHeight()`, if `fraction == 1.0f`, it pushes subsequent items (`Spacer`, `Text`) out of bounds.
  - Always wrap the bar in `Box(Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.BottomCenter)`.
- **Iteration in Composables**:
  - Never call `@Composable` functions inside standard `.forEach { ... }` lambdas.
  - Always use a standard `for (item in items) { ... }` loop or `items(items) { ... }` in a `LazyColumn` / `LazyRow`.
- **Top-Level Navigation**:
  - Main app uses 5 primary navigation tabs: `Dashboard`, `Expenses`, `Budgets`, `Analytics`, `AI Advisor`.
  - Floating Action Button (FAB) triggers Quick Log expense modal sheet.
  - AI Advisor is a dedicated top-level screen (`AIAdvisorScreen.kt`) featuring the Financial Wellness Index gauge, 50/30/20 wealth allocation, recurring subscription audit, and interactive Gemini Spend Intelligence chat thread.

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

## 7. Device Testing & UI Automator via USB ADB
- Check attached device: `adb devices`
- Stream install APK: `adb install -r android/app/build/outputs/apk/debug/app-debug.apk`
- Bring MainActivity to front: `adb shell am start -n com.expenseflow.app/.MainActivity`
- **OnePlus Physical Device (1080×2400) Coordinate Reference**:
  - Bottom Navigation Bar ($y \in [2240, 2384]$):
    - Tab 0 (Dashboard): `x=125, y=2312`
    - Tab 1 (Expenses): `x=340, y=2312`
    - Tab 2 (Budgets): `x=546, y=2312`
    - Tab 3 (Analytics): `x=751, y=2312`
    - Tab 4 (AI Advisor): `x=960, y=2312`
  - Quick Log FAB: `x=948, y=2091`
  - Set Target Button (Budgets header): `x=812, y=380`
- **Soft Keyboard (IME) Handling in ADB**:
  - `adb shell input keyevent 4` (Back) dismisses `ModalBottomSheet` rather than just the soft keyboard.
  - To dismiss keyboard without closing the sheet, tap the keyboard collapse chevron at `x=95, y=2365` or use `adb shell input keyevent 111` (Escape).

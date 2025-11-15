# ProSite Mobile - Flutter Application

ProSite Mobile is a cross-platform mobile application for construction quality management, built with Flutter.

## Features

### Core Modules
- ✅ **Authentication** - Login, registration, password reset
- ✅ **Dashboard** - KPIs, charts, quick actions
- ✅ **Batch Entry** - Record concrete deliveries with photos
- ✅ **Cube Tests** - Record test results, digital signatures
- ✅ **Material Vehicle Register** - Track vehicle entry/exit
- ✅ **Training** - TBT attendance via QR code scanning
- ✅ **Safety NC** - Raise non-conformances with photos
- ✅ **PTW (Permit to Work)** - Digital permit workflow
- ✅ **Reports** - Generate and view QC reports

### Key Features
- 📱 **Offline Support** - Work without internet, sync later
- 📷 **Camera Integration** - Capture photos for batches, NCs
- 🔍 **QR Code Scanning** - Training attendance, asset tracking
- 🖊️ **Digital Signatures** - Sign tests and permits
- 📊 **Charts & Analytics** - Real-time KPIs and trends
- 🔔 **Push Notifications** - Alerts for test failures, approvals
- 🌍 **Geolocation** - Track batch delivery locations
- 🗂️ **Document Management** - Upload PDFs, images

## Architecture

```
prosite_mobile/
├── lib/
│   ├── main.dart                  # App entry point
│   ├── app.dart                   # MaterialApp configuration
│   ├── config/
│   │   ├── api_config.dart        # API endpoints
│   │   ├── theme_config.dart      # App theme
│   │   └── constants.dart         # App constants
│   ├── models/                    # Data models
│   │   ├── user.dart
│   │   ├── batch.dart
│   │   ├── cube_test.dart
│   │   ├── safety_nc.dart
│   │   └── project.dart
│   ├── services/                  # Business logic
│   │   ├── auth_service.dart      # Authentication
│   │   ├── api_service.dart       # HTTP requests
│   │   ├── storage_service.dart   # Local storage
│   │   ├── sync_service.dart      # Offline sync
│   │   └── location_service.dart  # GPS
│   ├── providers/                 # State management (Provider pattern)
│   │   ├── auth_provider.dart
│   │   ├── batch_provider.dart
│   │   ├── project_provider.dart
│   │   └── sync_provider.dart
│   ├── screens/                   # UI screens
│   │   ├── auth/
│   │   │   ├── login_screen.dart
│   │   │   ├── register_screen.dart
│   │   │   └── forgot_password_screen.dart
│   │   ├── dashboard/
│   │   │   └── dashboard_screen.dart
│   │   ├── batches/
│   │   │   ├── batch_list_screen.dart
│   │   │   ├── batch_entry_screen.dart
│   │   │   └── batch_detail_screen.dart
│   │   ├── cube_tests/
│   │   │   ├── test_list_screen.dart
│   │   │   ├── test_entry_screen.dart
│   │   │   └── test_detail_screen.dart
│   │   ├── safety/
│   │   │   ├── nc_list_screen.dart
│   │   │   ├── nc_entry_screen.dart
│   │   │   ├── ptw_list_screen.dart
│   │   │   └── ptw_entry_screen.dart
│   │   ├── training/
│   │   │   ├── tbt_list_screen.dart
│   │   │   └── tbt_attendance_screen.dart
│   │   └── profile/
│   │       └── profile_screen.dart
│   ├── widgets/                   # Reusable widgets
│   │   ├── custom_button.dart
│   │   ├── custom_text_field.dart
│   │   ├── photo_picker.dart
│   │   ├── signature_pad.dart
│   │   ├── qr_scanner.dart
│   │   └── chart_widgets.dart
│   └── utils/                     # Helper functions
│       ├── validators.dart
│       ├── date_formatter.dart
│       └── permission_helper.dart
├── assets/
│   ├── images/
│   │   └── logo.png
│   └── fonts/
│       └── Roboto-Regular.ttf
├── android/                       # Android configuration
├── ios/                           # iOS configuration
├── pubspec.yaml                   # Dependencies
└── README.md                      # This file
```

## Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  provider: ^6.1.1
  
  # HTTP & API
  http: ^1.1.0
  dio: ^5.4.0
  
  # Local Storage
  sqflite: ^2.3.0
  shared_preferences: ^2.2.2
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  
  # Camera & Media
  image_picker: ^1.0.4
  camera: ^0.10.5+5
  
  # QR Code
  qr_code_scanner: ^1.0.1
  qr_flutter: ^4.1.0
  
  # Signatures
  signature: ^5.4.0
  
  # Location
  geolocator: ^10.1.0
  geocoding: ^2.1.1
  
  # Charts
  fl_chart: ^0.65.0
  syncfusion_flutter_charts: ^23.2.7
  
  # Notifications
  firebase_messaging: ^14.7.6
  flutter_local_notifications: ^16.3.0
  
  # File Handling
  path_provider: ^2.1.1
  file_picker: ^6.1.1
  pdf: ^3.10.7
  
  # UI Components
  intl: ^0.18.1
  cached_network_image: ^3.3.0
  shimmer: ^3.0.0
  flutter_spinkit: ^5.2.0
  
  # Utilities
  connectivity_plus: ^5.0.2
  permission_handler: ^11.1.0
  flutter_secure_storage: ^9.0.0
```

## Setup Instructions

### Prerequisites
- Flutter SDK (3.16.0 or higher)
- Dart SDK (3.2.0 or higher)
- Android Studio / Xcode
- VS Code with Flutter extensions

### Installation

1. **Install Flutter**
   ```bash
   # macOS
   brew install flutter
   
   # Ubuntu/Linux
   snap install flutter --classic
   
   # Windows
   # Download from https://flutter.dev
   ```

2. **Clone Repository**
   ```bash
   cd /workspaces/concretethings/prosite_mobile
   ```

3. **Install Dependencies**
   ```bash
   flutter pub get
   ```

4. **Configure API Endpoint**
   Edit `lib/config/api_config.dart`:
   ```dart
   class ApiConfig {
     static const String baseUrl = 'http://your-backend-url:8001/api';
     // or
     static const String baseUrl = 'https://your-domain.com/api';
   }
   ```

5. **Run App**
   ```bash
   # List available devices
   flutter devices
   
   # Run on specific device
   flutter run -d <device-id>
   
   # Run in debug mode
   flutter run
   
   # Build release APK
   flutter build apk --release
   
   # Build iOS (macOS only)
   flutter build ios --release
   ```

## API Integration

### Authentication
```dart
// Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "QualityEngineer"
  }
}
```

### Batch Entry
```dart
// Create batch
POST /api/batches/create
Headers: Authorization: Bearer <token>
{
  "project_id": 1,
  "mix_design_id": 1,
  "batch_number": "BATCH-2025-0001",
  "delivery_date": "2025-11-15",
  "quantity_received": 10.0,
  "slump_tested": 100.0,
  "temperature_celsius": 32.0,
  "latitude": 19.0760,
  "longitude": 72.8777
}
```

## Offline Mode

### How It Works
1. All data fetched from API is cached in local SQLite database
2. User can create/edit records offline
3. Records marked as `sync_status: 'pending'`
4. When online, SyncService automatically uploads pending records
5. Conflict resolution: Server timestamp wins

### Implementation
```dart
// Save to local DB
await StorageService.saveBatch(batch, syncStatus: 'pending');

// Sync when online
if (await ConnectivityService.isOnline()) {
  await SyncService.syncPendingBatches();
}
```

## Screenshots

(Add screenshots here after building the app)

## Testing

```bash
# Run unit tests
flutter test

# Run integration tests
flutter test integration_test/

# Run with coverage
flutter test --coverage
```

## Build & Release

### Android
```bash
# Build APK
flutter build apk --release

# Build App Bundle (for Play Store)
flutter build appbundle --release

# Output: build/app/outputs/flutter-apk/app-release.apk
```

### iOS
```bash
# Build iOS
flutter build ios --release

# Archive for App Store
# Open Xcode, Archive → Upload to App Store
```

## Troubleshooting

### Common Issues

1. **Camera not working**
   - Add permissions in `AndroidManifest.xml` and `Info.plist`
   
2. **Location not working**
   - Enable GPS permissions
   - Check location services enabled

3. **Build fails**
   - Run `flutter clean && flutter pub get`
   - Check Flutter doctor: `flutter doctor -v`

## Roadmap

- [ ] v1.0 - Core modules (Batches, Tests, Safety NC)
- [ ] v1.1 - Offline sync
- [ ] v1.2 - Push notifications
- [ ] v1.3 - Advanced analytics
- [ ] v1.4 - Biometric authentication
- [ ] v1.5 - Multi-language support

## Support

For issues, contact: support@prosite.com

## License

Proprietary - All rights reserved

---

**Built with** ❤️ **using Flutter**

# 🚀 ProSite Mobile - Flutter App Complete Guide

## ✅ Project Structure Created

```
prosite_mobile/
├── README.md              ✅ Complete documentation
├── pubspec.yaml           ✅ All dependencies configured
├── lib/
│   ├── main.dart          ✅ App entry point
│   ├── app.dart          ⏳ MaterialApp configuration (see below)
│   ├── config/           ⏳ API config, theme, constants
│   ├── models/           ⏳ Data models (User, Batch, Test, etc.)
│   ├── services/         ⏳ API, storage, sync services
│   ├── providers/        ⏳ State management
│   ├── screens/          ⏳ UI screens
│   ├── widgets/          ⏳ Reusable components
│   └── utils/            ⏳ Helper functions
├── assets/               ✅ Created
│   ├── images/
│   ├── icons/
│   ├── lottie/
│   └── fonts/
└── android/              ⏳ Android configuration
└── ios/                  ⏳ iOS configuration
```

## 📱 Key Files to Complete

### 1. lib/app.dart
```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/theme_config.dart';
import 'providers/auth_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/dashboard/dashboard_screen.dart';
import 'screens/splash_screen.dart';

class ProSiteApp extends StatelessWidget {
  const ProSiteApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ProSite Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeConfig.lightTheme,
      darkTheme: ThemeConfig.darkTheme,
      home: Consumer<AuthProvider>(
        builder: (context, auth, _) {
          if (auth.isLoading) {
            return const SplashScreen();
          }
          return auth.isAuthenticated 
              ? const DashboardScreen() 
              : const LoginScreen();
        },
      ),
      routes: {
        '/login': (context) => const LoginScreen(),
        '/dashboard': (context) => const DashboardScreen(),
        '/batches': (context) => const BatchListScreen(),
        '/cube-tests': (context) => const TestListScreen(),
        '/safety-nc': (context) => const SafetyNCListScreen(),
        '/profile': (context) => const ProfileScreen(),
      },
    );
  }
}
```

### 2. lib/config/api_config.dart
```dart
class ApiConfig {
  // Backend API URL
  static const String baseUrl = 'http://10.0.2.2:8001/api'; // Android emulator
  // static const String baseUrl = 'http://localhost:8001/api'; // iOS simulator
  // static const String baseUrl = 'https://your-domain.com/api'; // Production
  
  // Endpoints
  static const String login = '$baseUrl/auth/login';
  static const String register = '$baseUrl/auth/register';
  static const String forgotPassword = '$baseUrl/auth/forgot-password';
  
  static const String batches = '$baseUrl/batches';
  static const String cubeTests = '$baseUrl/cube-tests';
  static const String safetyNC = '$baseUrl/safety-nc';
  static const String ptw = '$baseUrl/work-permits';
  static const String tbt = '$baseUrl/tbt-sessions';
  static const String materials = '$baseUrl/material-vehicle-register';
  
  // Timeout
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}
```

### 3. lib/config/theme_config.dart
```dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class ThemeConfig {
  static const Color primaryColor = Color(0xFF3B82F6); // Blue
  static const Color secondaryColor = Color(0xFF10B981); // Green
  static const Color errorColor = Color(0xFFEF4444); // Red
  static const Color warningColor = Color(0xFFF59E0B); // Orange
  
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        brightness: Brightness.light,
      ),
      textTheme: GoogleFonts.robotoTextTheme(),
      appBarTheme: const AppBarTheme(
        elevation: 0,
        centerTitle: true,
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      cardTheme: CardTheme(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }
  
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        brightness: Brightness.dark,
      ),
      textTheme: GoogleFonts.robotoTextTheme(ThemeData.dark().textTheme),
    );
  }
}
```

### 4. lib/models/user.dart
```dart
class User {
  final int id;
  final String email;
  final String fullName;
  final String? phone;
  final String? designation;
  final int companyId;
  final String? role;
  final bool isActive;
  
  User({
    required this.id,
    required this.email,
    required this.fullName,
    this.phone,
    this.designation,
    required this.companyId,
    this.role,
    this.isActive = true,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      fullName: json['full_name'],
      phone: json['phone'],
      designation: json['designation'],
      companyId: json['company_id'],
      role: json['role'],
      isActive: json['is_active'] ?? true,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'phone': phone,
      'designation': designation,
      'company_id': companyId,
      'role': role,
      'is_active': isActive,
    };
  }
}
```

### 5. lib/models/batch.dart
```dart
class Batch {
  final int? id;
  final int projectId;
  final int mixDesignId;
  final String batchNumber;
  final String deliveryDate;
  final String deliveryTime;
  final double quantityOrdered;
  final double quantityReceived;
  final String vehicleNumber;
  final String? driverName;
  final double? temperatureCelsius;
  final double? slumpTested;
  final String? buildingName;
  final String? floorLevel;
  final String? structuralElementType;
  final double? latitude;
  final double? longitude;
  final String? verificationStatus;
  final String? batchSheetPhotoPath;
  final DateTime createdAt;
  
  Batch({
    this.id,
    required this.projectId,
    required this.mixDesignId,
    required this.batchNumber,
    required this.deliveryDate,
    required this.deliveryTime,
    required this.quantityOrdered,
    required this.quantityReceived,
    required this.vehicleNumber,
    this.driverName,
    this.temperatureCelsius,
    this.slumpTested,
    this.buildingName,
    this.floorLevel,
    this.structuralElementType,
    this.latitude,
    this.longitude,
    this.verificationStatus = 'pending',
    this.batchSheetPhotoPath,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();
  
  factory Batch.fromJson(Map<String, dynamic> json) {
    return Batch(
      id: json['id'],
      projectId: json['project_id'],
      mixDesignId: json['mix_design_id'],
      batchNumber: json['batch_number'],
      deliveryDate: json['delivery_date'],
      deliveryTime: json['delivery_time'],
      quantityOrdered: (json['quantity_ordered'] as num).toDouble(),
      quantityReceived: (json['quantity_received'] as num).toDouble(),
      vehicleNumber: json['vehicle_number'],
      driverName: json['driver_name'],
      temperatureCelsius: json['temperature_celsius']?.toDouble(),
      slumpTested: json['slump_tested']?.toDouble(),
      buildingName: json['building_name'],
      floorLevel: json['floor_level'],
      structuralElementType: json['structural_element_type'],
      latitude: json['latitude']?.toDouble(),
      longitude: json['longitude']?.toDouble(),
      verificationStatus: json['verification_status'],
      batchSheetPhotoPath: json['batch_sheet_photo_name'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'project_id': projectId,
      'mix_design_id': mixDesignId,
      'batch_number': batchNumber,
      'delivery_date': deliveryDate,
      'delivery_time': deliveryTime,
      'quantity_ordered': quantityOrdered,
      'quantity_received': quantityReceived,
      'vehicle_number': vehicleNumber,
      'driver_name': driverName,
      'temperature_celsius': temperatureCelsius,
      'slump_tested': slumpTested,
      'building_name': buildingName,
      'floor_level': floorLevel,
      'structural_element_type': structuralElementType,
      'latitude': latitude,
      'longitude': longitude,
      'verification_status': verificationStatus,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
```

### 6. lib/services/api_service.dart
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

class ApiService {
  static Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> body, {
    String? token,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(endpoint),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: json.encode(body),
      ).timeout(ApiConfig.connectionTimeout);
      
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return json.decode(response.body);
      } else {
        throw Exception('API Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network Error: $e');
    }
  }
  
  static Future<Map<String, dynamic>> get(
    String endpoint, {
    String? token,
    Map<String, String>? queryParams,
  }) async {
    try {
      var uri = Uri.parse(endpoint);
      if (queryParams != null) {
        uri = uri.replace(queryParameters: queryParams);
      }
      
      final response = await http.get(
        uri,
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
      ).timeout(ApiConfig.receiveTimeout);
      
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return json.decode(response.body);
      } else {
        throw Exception('API Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network Error: $e');
    }
  }
}
```

## 🎨 Complete Screens to Implement

1. **Login Screen** (`screens/auth/login_screen.dart`)
   - Email/password fields
   - Remember me checkbox
   - Forgot password link
   - Login button with loading state

2. **Dashboard Screen** (`screens/dashboard/dashboard_screen.dart`)
   - KPI cards (batches, tests, NCs)
   - Quick action buttons
   - Recent activity list
   - Charts (batches trend, test results)

3. **Batch Entry Screen** (`screens/batches/batch_entry_screen.dart`)
   - Form fields for batch details
   - Camera for batch sheet photo
   - GPS location capture
   - Slump test input
   - Submit button

4. **Cube Test Screen** (`screens/cube_tests/test_entry_screen.dart`)
   - Test date picker
   - Compressive strength input
   - Pass/Fail indicator
   - Digital signature pad
   - Photo capture

5. **Safety NC Screen** (`screens/safety/nc_entry_screen.dart`)
   - NC description
   - Severity dropdown
   - Location
   - Photo gallery (multiple)
   - Corrective action field

## 🔧 Build Commands

```bash
# Create Flutter project (if not done)
flutter create prosite_mobile

# Get dependencies
cd prosite_mobile
flutter pub get

# Run on Android emulator
flutter run

# Build Android APK
flutter build apk --release

# Build Android App Bundle
flutter build appbundle --release

# Build iOS (macOS only)
flutter build ios --release
```

## 📦 Next Steps

1. ✅ Project structure created
2. ⏳ Run `flutter pub get` to install dependencies
3. ⏳ Complete all model classes (User, Batch, CubeTest, SafetyNC, etc.)
4. ⏳ Implement all service classes (API, Storage, Sync)
5. ⏳ Create all provider classes for state management
6. ⏳ Build all UI screens
7. ⏳ Implement offline sync logic
8. ⏳ Add camera and QR code scanning
9. ⏳ Configure Android/iOS permissions
10. ⏳ Test on physical devices
11. ⏳ Build and release APK/IPA

## 🎯 Estimated Development Time

- Core structure & setup: **2 days** ✅
- Models & services: **3 days**
- UI screens: **5 days**
- State management: **2 days**
- Offline sync: **3 days**
- Camera & media: **2 days**
- Testing & bug fixes: **3 days**
- **Total: ~20 days** (1 developer)

## 📞 Support

For questions or issues, refer to:
- Flutter documentation: https://flutter.dev/docs
- ProSite backend API: `BACKEND_COMPLETE_SUMMARY.md`
- User roles: `DEMO_USERS_GUIDE.md`

---

**Status**: Project structure complete ✅  
**Next**: Install dependencies and start coding!

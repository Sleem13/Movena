import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:intl/intl.dart';

import '../generated/messages.dart';
import '../generated/tokens.dart';
import '../generated/exercise_names.dart';

class Preferences extends ChangeNotifier {
  String language = 'en';
  ThemeMode themeMode = ThemeMode.system;
  String t(String key) =>
      messages[language]?[key] ?? messages['en']?[key] ?? key;
  String exerciseName(String id) =>
      exerciseNames[id]?[language] ?? id.replaceAll('_', ' ');
  String number(num value) =>
      NumberFormat.decimalPattern(language).format(value);
  String date(String value) {
    final parsed = DateTime.tryParse(value);
    return parsed == null
        ? t('unavailable')
        : DateFormat.yMMMd(language).format(parsed);
  }

  String timestampDate(String value) {
    // Legacy timestamp fields without offsets are UTC, unlike calendar dates.
    final zoned = RegExp(r'(Z|[+-]\d{2}:\d{2})$').hasMatch(value)
        ? value
        : '${value}Z';
    final parsed = DateTime.tryParse(zoned);
    return parsed == null
        ? t('unavailable')
        : DateFormat.yMMMd(language).format(parsed.toLocal());
  }

  Future<void> restore() async {
    final store = await SharedPreferences.getInstance();
    language = store.getString('movena_locale') == 'ar' ? 'ar' : 'en';
    themeMode = ThemeMode.values.firstWhere(
      (v) => v.name == store.getString('movena_theme'),
      orElse: () => ThemeMode.system,
    );
    notifyListeners();
  }

  Future<void> setLanguage(String value) async {
    language = value == 'ar' ? 'ar' : 'en';
    notifyListeners();
    await (await SharedPreferences.getInstance()).setString(
      'movena_locale',
      language,
    );
  }

  Future<void> setTheme(ThemeMode value) async {
    themeMode = value;
    notifyListeners();
    await (await SharedPreferences.getInstance()).setString(
      'movena_theme',
      value.name,
    );
  }
}

ThemeData movenaTheme(Brightness brightness) {
  final colors =
      (designTokens['colors'] as Map)[brightness == Brightness.dark
              ? 'dark'
              : 'light']
          as Map;
  Color c(String key) => Color(
    int.parse((colors[key] as String).replaceFirst('#', 'FF'), radix: 16),
  );
  final scheme =
      ColorScheme.fromSeed(
        seedColor: c('primary'),
        brightness: brightness,
      ).copyWith(
        primary: c('primary'),
        onPrimary: c('onPrimary'),
        surface: c('surface'),
        onSurface: c('text'),
        error: c('danger'),
      );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: c('background'),
    appBarTheme: AppBarTheme(
      backgroundColor: c('surface'),
      foregroundColor: c('text'),
      centerTitle: false,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: const Size(48, 52),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(48, 52),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: c('surface'),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      contentPadding: const EdgeInsets.all(16),
    ),
    cardTheme: CardThemeData(
      color: c('surface'),
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: BorderSide(color: c('border')),
      ),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: c('surface'),
      indicatorColor: c('tint'),
    ),
    textTheme: Typography.material2021().black
        .apply(bodyColor: c('text'), displayColor: c('text'))
        .copyWith(
          headlineLarge: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.w800,
            height: 1.2,
            color: c('text'),
          ),
          titleLarge: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w700,
            color: c('text'),
          ),
        ),
  );
}

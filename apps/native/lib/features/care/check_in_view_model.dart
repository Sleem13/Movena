import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import 'care_repository.dart';

/// Owns mutation state and retry identity; clinical rules remain on the server.
class CheckInViewModel extends ChangeNotifier {
  final CareRepository repository;
  CheckInViewModel(this.repository);
  bool busy = false, saved = false, _disposed = false;
  String? error, _payload, _key;
  void _notify() {
    if (!_disposed) notifyListeners();
  }

  Future<void> save(Map<String, dynamic> values) async {
    if (busy || saved || _disposed) return;
    final payload = jsonEncode(values);
    if (payload != _payload) {
      _payload = payload;
      _key = const Uuid().v4();
    }
    busy = true;
    error = null;
    _notify();
    try {
      await repository.saveCheckIn(values, _key!);
      saved = true;
    } catch (e) {
      error = e.toString();
    } finally {
      busy = false;
      _notify();
    }
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}

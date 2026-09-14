import 'dart:convert';

import 'package:flutter/foundation.dart';

import '../../core/api_client.dart';

bool validNewPassword(String value) =>
    value.runes.length >= 8 && utf8.encode(value).length <= 72;

class AccountLink {
  final String mode, token;
  const AccountLink(this.mode, this.token);
  static AccountLink? parse(Uri uri) {
    if (uri.scheme != 'movena' || uri.userInfo.isNotEmpty || uri.hasPort) {
      return null;
    }
    final mode = uri.host.isNotEmpty
        ? uri.host
        : uri.path.replaceFirst(RegExp(r'^/'), '');
    if (!['verify-email', 'reset-password'].contains(mode) ||
        (uri.host.isNotEmpty && uri.path.isNotEmpty && uri.path != '/')) {
      return null;
    }
    final token = uri.queryParameters['token'] ?? '';
    if (token.length < 32 ||
        token.length > 512 ||
        RegExp(r'\s').hasMatch(token)) {
      return null;
    }
    return AccountLink(mode, token);
  }
}

class AccountViewModel extends ChangeNotifier {
  final ApiClient api;
  bool busy = false, done = false, _disposed = false;
  String? error, errorKey, successKey;
  AccountViewModel(this.api);
  void notify() {
    if (!_disposed) notifyListeners();
  }

  Future<void> submit(String mode, Map<String, dynamic> body) async {
    if (busy || done) return;
    busy = true;
    error = null;
    errorKey = null;
    notify();
    try {
      final result = objectOf(
        await api.request('auth/$mode', method: 'POST', body: body),
      );
      successKey = mode == 'register'
          ? (result['is_verified'] == true ? 'accountCreated' : 'checkEmail')
          : mode == 'reset-password'
          ? 'passwordResetDone'
          : mode == 'verify-email'
          ? 'emailVerified'
          : 'sent';
      done = true;
    } catch (e) {
      error = e.toString();
      errorKey = e is ApiFailure && e.code == 'INVALID_OR_EXPIRED_TOKEN'
          ? 'invalidAccountLink'
          : e is ApiFailure &&
                e.code == 'EMAIL_DELIVERY_FAILED' &&
                mode == 'register'
          ? 'accountDeliveryFailed'
          : e is ApiFailure && e.code == 'EMAIL_ALREADY_REGISTERED'
          ? 'emailExists'
          : e is ApiFailure && e.code == 'USERNAME_ALREADY_REGISTERED'
          ? 'usernameExists'
          : 'accountError';
    } finally {
      busy = false;
      notify();
    }
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}

import 'package:flutter/foundation.dart';

import 'api_client.dart';
import '../generated/client.dart';

class SessionRepository extends ChangeNotifier {
  final ApiClient api;
  Map<String, dynamic>? user;
  bool loading = true;
  String? error;
  SessionRepository(this.api) {
    api.onUnauthorized = () {
      user = null;
      notifyListeners();
    };
  }
  Future<void> restore() async {
    try {
      if (await api.tokens.read() != null) {
        user = (await CoreApi(api.request).getCurrentUser()).toJson();
      }
    } catch (e) {
      error = e.toString();
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> login(String email, String password) async {
    final response = objectOf(
      await api.request(
        'auth/login',
        method: 'POST',
        body: {'email': email, 'password': password},
      ),
    );
    final token = response['access_token'];
    if (token is! String || token.isEmpty) {
      throw const ApiFailure('Invalid authentication response.');
    }
    final profile = objectOf(response['user']);
    await api.tokens.write(token);
    user = profile;
    error = null;
    notifyListeners();
  }

  Future<void> logout() async {
    await api.request('auth/logout', method: 'POST');
    await api.tokens.clear();
    user = null;
    notifyListeners();
  }
}

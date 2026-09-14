import 'dart:async';
import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

abstract class TokenStore {
  Future<String?> read();
  Future<void> write(String token);
  Future<void> clear();
}

class SecureTokenStore implements TokenStore {
  final FlutterSecureStorage storage;
  const SecureTokenStore([this.storage = const FlutterSecureStorage()]);
  static const key = 'movena_session_v2';
  @override
  Future<String?> read() => storage.read(key: key);
  @override
  Future<void> write(String token) => storage.write(key: key, value: token);
  @override
  Future<void> clear() => storage.delete(key: key);
}

class ApiFailure implements Exception {
  final String message;
  final int status;
  final String? code;
  const ApiFailure(this.message, [this.status = 0, this.code]);
  @override
  String toString() => message;
}

class ApiClient {
  final Uri origin;
  final TokenStore tokens;
  final http.Client client;
  void Function()? onUnauthorized;
  ApiClient(String base, this.tokens, {http.Client? client})
    : origin = Uri.parse(base),
      client = client ?? http.Client() {
    if (!['https', 'http'].contains(origin.scheme) ||
        origin.host.isEmpty ||
        origin.userInfo.isNotEmpty ||
        origin.hasQuery ||
        origin.hasFragment ||
        (origin.path.isNotEmpty && origin.path != '/')) {
      throw const ApiFailure('Configure a valid Movena API origin.');
    }
  }
  Uri uri(String path) {
    if (path.startsWith('/') || path.contains('..') || path.contains('://')) {
      throw const ApiFailure('Invalid API path.');
    }
    return origin.resolve('/api/v2/$path');
  }

  Future<dynamic> request(
    String path, {
    String method = 'GET',
    Object? body,
    String? idempotencyKey,
  }) async {
    final token = await tokens.read();
    final request = http.Request(method, uri(path));
    request.followRedirects = false;
    request.headers['Accept'] = 'application/json';
    if (token != null && !path.startsWith('auth/login')) {
      request.headers['Authorization'] = 'Bearer $token';
    }
    if (body != null) {
      request.headers['Content-Type'] = 'application/json';
      request.body = jsonEncode(body);
    }
    if (idempotencyKey != null) {
      request.headers['Idempotency-Key'] = idempotencyKey;
    }
    try {
      final response = await http.Response.fromStream(
        await client.send(request),
      ).timeout(const Duration(seconds: 40));
      return await decode(response);
    } on TimeoutException {
      throw const ApiFailure('The request timed out. Please try again.');
    } on http.ClientException {
      throw const ApiFailure(
        'Could not connect. Check your connection and try again.',
      );
    }
  }

  Future<dynamic> decode(http.Response response) async {
    if (response.statusCode == 401) {
      await tokens.clear();
      onUnauthorized?.call();
    }
    dynamic body;
    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw ApiFailure('The response could not be read.', response.statusCode);
    }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiFailure(
        body is Map
            ? (body['message']?.toString() ??
                  'The request could not be completed.')
            : 'The request could not be completed.',
        response.statusCode,
        body is Map ? body['error_code']?.toString() : null,
      );
    }
    return body;
  }

  void close() => client.close();
}

Map<String, dynamic> objectOf(dynamic data) {
  if (data is! Map<String, dynamic>) {
    throw const ApiFailure('The response has an unexpected format.');
  }
  return data;
}

List<Map<String, dynamic>> rowsOf(dynamic data) {
  if (data is! List) {
    throw const ApiFailure('The response has an unexpected format.');
  }
  return data.map(objectOf).toList();
}

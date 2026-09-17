import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:movena_native/core/api_client.dart';
import 'package:movena_native/features/account/data_rights_model.dart';

import 'recovery_test.dart' show MemoryTokens;

void main() {
  test(
    'data rights submission retains one retry key and nulls blank details',
    () async {
      final seen = <http.Request>[];
      final api = ApiClient(
        'http://localhost:8020',
        MemoryTokens(),
        client: MockClient((request) async {
          seen.add(request);
          return http.Response(
            '{"request_id":"r","request_type":"export","status":"pending","created_at":"2026-09-14T00:00:00Z"}',
            201,
          );
        }),
      );
      final repo = DataRightsRepository(api);
      const key = 'privacy-retry';
      await repo.create('export', '   ', key);
      await repo.create('export', '   ', key);
      expect(seen.every((r) => r.headers['Idempotency-Key'] == key), isTrue);
      expect(jsonDecode(seen.first.body)['details'], isNull);
      expect(validDataRightsDetails(List.filled(2000, 'x').join()), isTrue);
      expect(validDataRightsDetails(List.filled(2001, 'x').join()), isFalse);
    },
  );
}

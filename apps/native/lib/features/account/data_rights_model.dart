import 'dart:math';

import '../../core/api_client.dart';

bool validDataRightsDetails(String value) => value.trim().length <= 2000;
String newDataRightsKey() =>
    'privacy-${DateTime.now().microsecondsSinceEpoch}-${Random.secure().nextInt(1 << 32)}';

class DataRightsRepository {
  final ApiClient api;
  DataRightsRepository(this.api);
  Future<List<Map<String, dynamic>>> patientRequests() async =>
      rowsOf(await api.request('patient/data-rights-requests'));
  Future<void> create(String type, String details, String key) => api.request(
    'patient/data-rights-requests',
    method: 'POST',
    idempotencyKey: key,
    body: {
      'request_type': type,
      'details': details.trim().isEmpty ? null : details.trim(),
    },
  );
  Future<List<Map<String, dynamic>>> adminQueue() async =>
      rowsOf(await api.request('admin/platform/data-rights-requests'));
  Future<void> review(String id, String decision, String reason) => api.request(
    'admin/platform/data-rights-requests/${Uri.encodeComponent(id)}',
    method: 'PATCH',
    body: {'decision': decision, 'reason': reason.trim()},
  );
}

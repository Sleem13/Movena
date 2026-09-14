import 'package:flutter/foundation.dart';

import '../../core/api_client.dart';
import '../../generated/client.dart';
import '../../generated/models.dart';

const healthFields = <(String, String, int)>[
  ('emergency_contact_name', 'emergencyContactName', 120),
  ('emergency_contact_phone', 'emergencyContactPhone', 32),
  ('medical_summary', 'medicalSummary', 5000),
  ('precautions', 'precautions', 5000),
];

String? notificationDestination(String? value) => const {
  '/patient': 'today',
  '/patient/today': 'today',
  '/appointments': 'schedule',
  '/patient/appointments': 'schedule',
  '/connections': 'care',
}[value];

class PatientAccountRepository {
  final CoreApi core;
  PatientAccountRepository(ApiClient api) : core = CoreApi(api.request);
  Future<PatientHealthProfile> save(Map<String, String> values) =>
      core.updateHealthProfile(
        PatientHealthProfileUpdate.fromJson({
          for (final field in healthFields)
            field.$1: (values[field.$1] ?? '').trim().isEmpty
                ? null
                : values[field.$1]!.trim(),
        }),
      );
}

class HealthProfileModel extends ChangeNotifier {
  final PatientAccountRepository repository;
  bool busy = false, saved = false, _disposed = false;
  String? error;
  HealthProfileModel(this.repository);
  void changed() {
    saved = false;
    notify();
  }

  void notify() {
    if (!_disposed) notifyListeners();
  }

  Future<void> save(Map<String, String> values) async {
    if (busy) return;
    busy = true;
    saved = false;
    error = null;
    notify();
    try {
      await repository.save(values);
      saved = true;
    } catch (e) {
      error = e.toString();
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

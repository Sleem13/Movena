import '../../core/api_client.dart';
import '../../generated/client.dart';
import '../../generated/models.dart';

class CareRepository {
  final ApiClient api;
  CareRepository(this.api);
  Future<PatientTodayResponse> today() => CoreApi(api.request).getToday();
  Future<AdherenceDetail> saveCheckIn(
    Map<String, dynamic> values,
    String key,
  ) => CoreApi(api.request).saveCheckIn(AdherenceCreate.fromJson(values), key);
  Future<void> review(
    String patientId,
    String adherenceId,
    Map<String, dynamic> values,
  ) async {
    await api.request(
      'therapist/patients/${Uri.encodeComponent(patientId)}/adherence/${Uri.encodeComponent(adherenceId)}/acknowledge',
      method: 'POST',
      body: ExerciseResponseReview.fromJson(values).toJson(),
    );
  }
}

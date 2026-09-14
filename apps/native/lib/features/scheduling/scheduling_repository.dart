import '../../core/api_client.dart';
import '../../generated/client.dart';
import '../../generated/models.dart';

class SchedulingRepository {
  final ApiClient api;
  SchedulingRepository(this.api);
  CoreApi get client => CoreApi(api.request);
  Future<List<AppointmentSummary>> appointments(String role) =>
      role == 'patient'
      ? client.getPatientAppointments()
      : client.getStaffAppointments();
  Future<List<Map<String, dynamic>>> connections() async =>
      rowsOf(await api.request('connections'))
          .where((row) => row['status'] == 'active')
          .toList();
  Future<AvailabilitySlots> slots(String therapist, String day) =>
      client.getAvailableSlots(therapist, day);
  Future<AppointmentSummary> book(Map<String, dynamic> values, String key) =>
      client.bookAppointment(AppointmentCreate.fromJson(values), key);
  Future<AppointmentSummary> update(String id, Map<String, dynamic> values) =>
      client.updateAppointment(id, AppointmentUpdate.fromJson(values));
  Future<AppointmentJoinResponse> join(String id) => client.joinAppointment(id);
  Future<List<AvailabilityDetail>> availability() => client.getAvailability();
  Future<void> addAvailability(Map<String, dynamic> values) async {
    await client.addAvailability(AvailabilityCreate.fromJson(values));
  }
}

String calendarDay(DateTime value) =>
    '${value.year}-${value.month.toString().padLeft(2, '0')}-${value.day.toString().padLeft(2, '0')}';

Uri visitUri(AppointmentJoinResponse grant, {DateTime? now}) {
  final uri = Uri.tryParse(grant.roomUrl);
  final expiry = DateTime.tryParse(grant.expiresAt);
  if (uri == null ||
      uri.scheme != 'https' ||
      uri.host.isEmpty ||
      uri.userInfo.isNotEmpty ||
      grant.meetingToken.isEmpty ||
      expiry == null ||
      !expiry.isAfter(now ?? DateTime.now())) {
    throw const ApiFailure(
      'The video link is unavailable or expired. Try again.',
    );
  }
  return uri.replace(
    queryParameters: {...uri.queryParameters, 't': grant.meetingToken},
  );
}

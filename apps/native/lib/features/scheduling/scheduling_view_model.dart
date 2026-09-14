import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import '../../generated/models.dart';
import 'scheduling_repository.dart';

class SchedulingViewModel extends ChangeNotifier {
  final SchedulingRepository repository;
  final String role;
  SchedulingViewModel(this.repository, this.role);
  List<AppointmentSummary> appointments = [];
  List<Map<String, dynamic>> connections = [];
  bool loading = true, busy = false, _disposed = false;
  String? error;
  int _revision = 0;
  void notify() {
    if (!_disposed) notifyListeners();
  }

  Future<void> load() async {
    final revision = ++_revision;
    loading = true;
    error = null;
    notify();
    try {
      final result = await Future.wait([
        repository.appointments(role),
        repository.connections(),
      ]);
      if (revision != _revision || _disposed) return;
      appointments = result[0] as List<AppointmentSummary>;
      connections = result[1] as List<Map<String, dynamic>>;
      appointments.sort((a, b) => a.startsAt.compareTo(b.startsAt));
    } catch (e) {
      if (revision == _revision) error = e.toString();
    } finally {
      if (revision == _revision) {
        loading = false;
        notify();
      }
    }
  }

  Future<bool> update(String id, Map<String, dynamic> values) async {
    if (busy) return false;
    busy = true;
    error = null;
    notify();
    try {
      await repository.update(id, values);
      await load();
      return true;
    } catch (e) {
      error = e.toString();
      return false;
    } finally {
      busy = false;
      notify();
    }
  }

  @override
  void dispose() {
    _disposed = true;
    _revision++;
    super.dispose();
  }
}

class BookingViewModel extends ChangeNotifier {
  final SchedulingRepository repository;
  BookingViewModel(this.repository);
  bool busy = false, loadingSlots = false, _disposed = false;
  String? error, _body, _key;
  List<AppointmentSlot> slots = [];
  AppointmentSlot? selected;
  AppointmentSummary? booked;
  int _revision = 0;
  void notify() {
    if (!_disposed) notifyListeners();
  }

  Future<void> loadSlots(String therapist, String day) async {
    final revision = ++_revision;
    selected = null;
    slots = [];
    error = null;
    loadingSlots = true;
    notify();
    try {
      final result = await repository.slots(therapist, day);
      if (revision == _revision && !_disposed) {
        slots = result.slots
            .where(
              (slot) => DateTime.parse(slot.startsAt).isAfter(DateTime.now()),
            )
            .toList();
      }
    } catch (e) {
      if (revision == _revision) error = e.toString();
    } finally {
      if (revision == _revision) {
        loadingSlots = false;
        notify();
      }
    }
  }

  void choose(AppointmentSlot slot) {
    if (busy) return;
    selected = slot;
    notify();
  }

  Future<void> book(Map<String, dynamic> connection, String mode) async {
    if (busy || selected == null || booked != null) return;
    final values = {
      'patient_id': connection['patient_id'],
      'therapist_user_id': connection['therapist_user_id'],
      'starts_at': selected!.startsAt,
      'ends_at': selected!.endsAt,
      'delivery_mode': mode,
    };
    final body = jsonEncode(values);
    if (body != _body) {
      _body = body;
      _key = const Uuid().v4();
    }
    busy = true;
    error = null;
    notify();
    try {
      booked = await repository.book(values, _key!);
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
    _revision++;
    super.dispose();
  }
}

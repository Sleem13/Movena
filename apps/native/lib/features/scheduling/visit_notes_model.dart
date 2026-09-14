import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import '../../core/api_client.dart';
import '../../generated/client.dart';
import '../../generated/models.dart';

class VisitNotesRepository {
  final ApiClient api;
  VisitNotesRepository(this.api);
  Future<List<ClinicalNoteDetail>> list(String id, bool staff) => staff
      ? CoreApi(api.request).getStaffVisitNotes(id)
      : CoreApi(api.request).getPatientVisitNotes(id);
  Future<ClinicalNoteDetail> create(
    String id,
    Map<String, dynamic> values,
    String key,
  ) =>
      CoreApi(api.request)
          .createVisitNote(id, ClinicalNoteCreate.fromJson(values), key);
}

class VisitNotesModel extends ChangeNotifier {
  final VisitNotesRepository repository;
  final String appointmentId;
  final bool staff;
  VisitNotesModel(this.repository, this.appointmentId, this.staff);
  List<ClinicalNoteDetail> notes = [];
  bool loading = false,
      busy = false,
      uncertain = false,
      saved = false,
      loaded = false;
  String? readError, saveError;
  Map<String, dynamic>? _body;
  String? _key;
  bool _disposed = false;
  int _revision = 0;
  void changed() {
    if (!_disposed) notifyListeners();
  }

  Future<void> load() async {
    final revision = ++_revision;
    loading = true;
    loaded = false;
    readError = null;
    notes = [];
    changed();
    try {
      final result = await repository.list(appointmentId, staff);
      if (!_disposed && revision == _revision) {
        notes = result;
        loaded = true;
      }
    } catch (e) {
      if (!_disposed && revision == _revision) readError = e.toString();
    } finally {
      if (!_disposed && revision == _revision) {
        loading = false;
        changed();
      }
    }
  }

  Future<bool> save(
    String summary,
    String recommendations,
    bool visible,
  ) async {
    if (busy || !staff || summary.trim().isEmpty) return false;
    final values = uncertain && _body != null
        ? _body!
        : <String, dynamic>{
            'summary': summary.trim(),
            'recommendations': recommendations.trim().isEmpty
                ? null
                : recommendations.trim(),
            'patient_visible': visible,
          };
    if (_body == null || jsonEncode(values) != jsonEncode(_body)) {
      _body = values;
      _key = const Uuid().v4();
    }
    busy = true;
    saveError = null;
    saved = false;
    changed();
    try {
      await repository.create(appointmentId, values, _key!);
      if (_disposed) return false;
      saved = true;
      uncertain = false;
      _body = null;
      _key = null;
      await load();
      return true;
    } catch (e) {
      if (!_disposed) {
        saveError = e.toString();
        final status = e is ApiFailure ? e.status : 0;
        uncertain = status == 0 || status == 409 || status >= 500;
      }
      return false;
    } finally {
      busy = false;
      changed();
    }
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}

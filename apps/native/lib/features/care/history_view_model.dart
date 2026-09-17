import 'package:flutter/foundation.dart';

import '../../core/api_client.dart';
import '../../generated/client.dart';
import '../../generated/models.dart';

const historyPageSize = 20;
const historyStatuses = ['', 'success', 'rejected', 'error'];
String historyStatusKey(String value) =>
    const {
      'success': 'historySuccess',
      'rejected': 'historyRejected',
      'error': 'historyError',
    }[value] ??
    'historyUnknown';
int? historyRepetitions(SessionSummary session) =>
    session.status == 'success' &&
        session.totalReps != null &&
        session.totalReps! >= 0
    ? session.totalReps
    : null;

class HistoryRepository {
  final ApiClient api;
  HistoryRepository(this.api);
  Future<SessionListResponse> page(int offset, String status) =>
      CoreApi(api.request).getSessionPage(historyPageSize, offset, status);
}

class HistoryViewModel extends ChangeNotifier {
  final HistoryRepository repository;
  HistoryViewModel(this.repository);
  int offset = 0;
  String status = '';
  SessionListResponse? data;
  String? error;
  bool busy = false;
  bool _disposed = false;
  int _request = 0;
  bool get hasOlder =>
      !busy && data != null && offset + historyPageSize < data!.total;
  Future<void> load() async {
    final request = ++_request;
    busy = true;
    error = null;
    data = null;
    notifyListeners();
    try {
      final result = await repository.page(offset, status);
      if (!_disposed && request == _request) data = result;
    } catch (e) {
      if (!_disposed && request == _request) error = e.toString();
    } finally {
      if (!_disposed && request == _request) {
        busy = false;
        notifyListeners();
      }
    }
  }

  Future<void> filter(String value) async {
    if (!historyStatuses.contains(value)) return;
    offset = 0;
    status = value;
    await load();
  }

  Future<void> older() async {
    if (hasOlder) {
      offset += historyPageSize;
      await load();
    }
  }

  Future<void> newer() async {
    if (offset > 0) {
      offset = (offset - historyPageSize).clamp(0, offset);
      await load();
    }
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}

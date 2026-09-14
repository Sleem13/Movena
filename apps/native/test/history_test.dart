import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:movena_native/core/preferences.dart';
import 'package:movena_native/features/care/history_view_model.dart';
import 'package:movena_native/features/analysis/analysis_view_model.dart';
import 'package:movena_native/features/care/progress_view.dart';
import 'package:movena_native/features/care/progress_reports_view.dart';
import 'package:movena_native/generated/models.dart';

import 'patient_account_test.dart' show makeApi;

Map<String, dynamic> session(String id, String status, int? reps) => {
  'session_id': id,
  'exercise_id': 'knee_extension',
  'exercise_display_name': 'Knee extension',
  'status': status,
  'created_at': '2026-09-13T12:00:00Z',
  'total_reps': reps,
};
http.Response page(String id, {int offset = 0, int total = 43}) =>
    http.Response(
      jsonEncode({
        'items': [session(id, 'success', 0)],
        'total': total,
        'limit': 20,
        'offset': offset,
      }),
      200,
    );
void main() {
  test('report URLs accept only safe web locations', () {
    final api = makeApi((_) async => http.Response('[]', 200));
    expect(
      reportUri(api, '/api/v1/artifacts/reports/id?id=one')?.toString(),
      'http://localhost:8020/api/v2/artifacts/reports/id?id=one',
    );
    expect(
      reportUri(api, 'https://files.movena.example/report?id=one'),
      isNotNull,
    );
    expect(reportUri(api, 'javascript:alert(1)'), isNull);
    expect(reportUri(api, 'https://user:secret@example.com/report'), isNull);
  });
  test('analysis restores an owned active job after relaunch', () async {
    final api = makeApi((request) async {
      expect(request.url.path, '/api/v2/analysis-jobs');
      return http.Response(
        jsonEncode([
          {
            'job_id': '00000000-0000-4000-8000-000000000401',
            'exercise_id': 'knee_extension',
            'status': 'running',
            'stage': 'pose',
            'progress': 40,
          },
        ]),
        200,
      );
    });
    final model = AnalysisViewModel(api);
    await model.restoreActive();
    expect(model.job?['status'], 'running');
    expect(model.exercise, 'knee_extension');
    model.dispose();
  });
  test(
    'history keeps page on offline retry and excludes non-success counts',
    () async {
      final offsets = <String>[];
      var fail = true;
      final model = HistoryViewModel(
        HistoryRepository(
          makeApi((request) async {
            final offset = request.url.queryParameters['offset']!;
            offsets.add(offset);
            expect(request.url.queryParameters['limit'], '20');
            if (offset == '20' && fail) {
              fail = false;
              return http.Response('{"message":"Offline"}', 503);
            }
            return page(offset, offset: int.parse(offset));
          }),
        ),
      );
      await model.load();
      expect(model.hasOlder, isTrue);
      await model.older();
      expect(model.offset, 20);
      expect(model.error, 'Offline');
      expect(model.data, isNull);
      await model.load();
      expect(model.data!.items.single.sessionId, '20');
      expect(offsets, ['0', '20', '20']);
      await model.filter('rejected');
      expect(model.offset, 0);
      for (final status in ['rejected', 'error', 'unknown']) {
        expect(
          historyRepetitions(SessionSummary.fromJson(session('x', status, 9))),
          isNull,
        );
      }
      expect(
        historyRepetitions(SessionSummary.fromJson(session('x', 'success', 0))),
        0,
      );
      expect(
        historyRepetitions(
          SessionSummary.fromJson(session('x', 'success', null)),
        ),
        isNull,
      );
      model.dispose();
    },
  );
  test(
    'stale history response cannot replace a newly selected outcome',
    () async {
      final pending = Completer<http.Response>();
      final model = HistoryViewModel(
        HistoryRepository(
          makeApi(
            (request) async => request.url.queryParameters['status'] == ''
                ? pending.future
                : page('filtered'),
          ),
        ),
      );
      final old = model.load();
      await model.filter('error');
      pending.complete(page('stale'));
      await old;
      expect(model.data!.items.single.sessionId, 'filtered');
      expect(model.status, 'error');
      model.dispose();
    },
  );
  testWidgets('Arabic history pages fit 320 pixels with 200 percent text', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 740);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final p = Preferences()..language = 'ar';
    final api = makeApi(
      (request) async => request.url.path.endsWith('/patient/reports')
          ? http.Response('[]', 200)
          : page(request.url.queryParameters['offset']!),
    );
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('ar'),
        supportedLocales: const [Locale('en'), Locale('ar')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        theme: movenaTheme(Brightness.dark),
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(context)
              .copyWith(textScaler: const TextScaler.linear(2)),
          child: child!,
        ),
        home: Scaffold(
          body: ProgressView(api: api, preferences: p),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    await tester.ensureVisible(find.text(p.t('historyOlder')));
    await tester.tap(find.text(p.t('historyOlder')));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    await tester.drag(find.byType(ListView), const Offset(0, -600));
    await tester.pumpAndSettle();
    expect(find.text('${p.number(0)} ${p.t('reps')}'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

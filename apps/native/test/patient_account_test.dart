import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:movena_native/core/api_client.dart';
import 'package:movena_native/core/preferences.dart';
import 'package:movena_native/features/account/patient_account_model.dart';
import 'package:movena_native/features/account/patient_account_view.dart';

import 'recovery_test.dart' show MemoryTokens;

ApiClient makeApi(Future<http.Response> Function(http.Request) handler) =>
    ApiClient(
      'http://localhost:8020',
      MemoryTokens(),
      client: MockClient(handler),
    );
void main() {
  test('health save keeps unknowns null and retries after failure', () async {
    var calls = 0;
    final bodies = <Map<String, dynamic>>[];
    final model = HealthProfileModel(
      PatientAccountRepository(
        makeApi((request) async {
          expect(request.method, 'PATCH');
          bodies.add(jsonDecode(request.body));
          calls++;
          return calls == 1
              ? http.Response('{"message":"Offline"}', 503)
              : http.Response('{"patient_id":"fixture"}', 200);
        }),
      ),
    );
    final values = {'medical_summary': ' Synthetic text ', 'precautions': '  '};
    await model.save(values);
    expect(model.saved, isFalse);
    expect(model.error, 'Offline');
    await model.save(values);
    expect(model.saved, isTrue);
    expect(bodies[0], bodies[1]);
    expect(bodies.last['precautions'], isNull);
    expect(bodies.last['medical_summary'], 'Synthetic text');
    expect(notificationDestination('/appointments'), 'schedule');
    for (final value in [
      '//example.test',
      'https://example.test',
      'javascript:alert(1)',
      '/patient/reports',
    ]) {
      expect(notificationDestination(value), isNull);
    }
    model.dispose();
  });
  testWidgets(
    'Arabic health editor fits a narrow screen with 200 percent text',
    (tester) async {
      tester.view.physicalSize = const Size(320, 740);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final p = Preferences()..language = 'ar';
      final client = makeApi(
        (request) async => http.Response(
          request.url.path.endsWith('consents')
              ? '[]'
              : '{"patient_id":"fixture","medical_summary":"Synthetic"}',
          200,
        ),
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
          home: HealthProfileView(api: client, preferences: p),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byType(TextFormField), findsNWidgets(4));
      expect(tester.takeException(), isNull);
      await tester.drag(
        find.byType(SingleChildScrollView),
        const Offset(0, -1200),
      );
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'notification read failure retains unread state and uses POST on retry',
    (tester) async {
      var writes = 0;
      final client = makeApi((request) async {
        if (request.url.path.endsWith('/read')) {
          expect(request.method, 'POST');
          writes++;
          return http.Response(
            writes == 1 ? ' {"message":"Offline"}' : '{"notification_id":"n","kind":"qa","title":"Fixture","body":"Body","created_at":"2026-09-13T12:00:00Z","read_at":"2026-09-13T12:01:00Z"}',
            writes == 1 ? 503 : 200,
          );
        }
        return http.Response(
          '[{"notification_id":"n","kind":"qa","title":"Fixture","body":"Body","created_at":"2026-09-13T12:00:00Z"}]',
          200,
        );
      });
      await tester.pumpWidget(
        MaterialApp(
          home: NotificationsView(api: client, preferences: Preferences()),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Mark as read'));
      await tester.pumpAndSettle();
      expect(find.text('Unread'), findsOneWidget);
      expect(find.text('Offline'), findsOneWidget);
      await tester.tap(find.text('Mark as read'));
      await tester.pumpAndSettle();
      expect(find.text('Read'), findsOneWidget);
      expect(find.text('Mark as read'), findsNothing);
    },
  );
}

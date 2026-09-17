import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:movena_native/core/api_client.dart';
import 'package:movena_native/core/preferences.dart';
import 'package:movena_native/core/session.dart';
import 'package:movena_native/main.dart';
import 'package:movena_native/features/care/today_view.dart';
import 'package:movena_native/features/care/review_form.dart';

class MemoryTokens implements TokenStore {
  String? value;
  @override
  Future<String?> read() async => value;
  @override
  Future<void> write(String token) async {
    value = token;
  }

  @override
  Future<void> clear() async {
    value = null;
  }
}

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });
  test(
    'revoked credentials clear native storage even for unreadable responses',
    () async {
      final store = MemoryTokens()..value = 'test-only-token';
      final api = ApiClient(
        'http://localhost:8020',
        store,
        client: MockClient((_) async => http.Response('unreadable', 401)),
      );
      await expectLater(api.request('auth/me'), throwsA(isA<ApiFailure>()));
      expect(store.value, isNull);
    },
  );
  test('tokens only travel to the configured origin and path traversal is rejected', () async {
    final store = MemoryTokens()..value = 'test-only-token';
    final api = ApiClient(
      'https://api.example.test',
      store,
      client: MockClient((request) async {
        expect(request.url.origin, 'https://api.example.test');
        expect(request.headers['Authorization'], 'Bearer test-only-token');
        return http.Response('{}', 200);
      }),
    );
    await api.request('patient/today');
    expect(() => api.uri('../secrets'), throwsA(isA<ApiFailure>()));
  });
  testWidgets(
    'login stores a session and renders only the patient navigation',
    (tester) async {
      tester.view.physicalSize = const Size(390, 844);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final tokens = MemoryTokens();
      final api = ApiClient(
        'http://localhost:8020',
        tokens,
        client: MockClient((request) async {
          if (request.url.path.endsWith('/auth/login')) {
            return http.Response(
              jsonEncode({
                'access_token': 'fixture-token',
                'user': {
                  'user_id': 'fixture-patient',
                  'role': 'patient',
                  'email': 'fixture@example.test',
                },
              }),
              200,
            );
          }
          return http.Response(
            jsonEncode({
              'patient_id': 'fixture-patient',
              'date': '2026-09-12',
              'plan_title': 'Fixture recovery plan',
              'plan_items': [],
              'unread_notifications': 0,
            }),
            200,
          );
        }),
      );
      final session = SessionRepository(api)..loading = false;
      final preferences = Preferences();
      await tester.pumpWidget(
        MovenaApp(session: session, preferences: preferences),
      );
      await tester.enterText(
        find.byType(TextFormField).at(0),
        'fixture@example.test',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'fixture-password',
      );
      await tester.ensureVisible(find.text('Log in'));
      await tester.tap(find.text('Log in'));
      await tester.pumpAndSettle();
      expect(tokens.value, 'fixture-token');
      expect(find.text('Today'), findsOneWidget);
      expect(find.text('Operations'), findsNothing);
      expect(find.text('Fixture recovery plan'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets('Arabic login uses RTL and remains usable on a narrow phone', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 700);
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final session = SessionRepository(
      ApiClient('http://localhost:8020', MemoryTokens()),
    )..loading = false;
    final preferences = Preferences()..language = 'ar';
    await tester.pumpWidget(
      MovenaApp(session: session, preferences: preferences),
    );
    await tester.pumpAndSettle();
    expect(find.text('تسجيل الدخول'), findsOneWidget);
    expect(
      Directionality.of(tester.element(find.byType(Form))),
      TextDirection.rtl,
    );
    expect(tester.takeException(), isNull);
  });
  testWidgets(
    'reopening a check-in preserves responses and requires symptom acknowledgement',
    (tester) async {
      tester.view.physicalSize = const Size(700, 2400);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      Map<String, dynamic>? saved;
      final api = ApiClient(
        'http://localhost:8020',
        MemoryTokens(),
        client: MockClient((request) async {
          saved = jsonDecode(request.body) as Map<String, dynamic>;
          expect(request.headers['Idempotency-Key'], isNotEmpty);
          return http.Response(
            jsonEncode({
              ...saved!,
              'adherence_id': 'response',
              'patient_id': 'fixture',
              'response_state': 'clinical_follow_up',
              'supportive_instruction': 'Synthetic instruction',
              'clinician_review_required': true,
              'created_at': '2026-09-12T00:00:00Z',
              'updated_at': '2026-09-12T00:00:00Z',
            }),
            201,
          );
        }),
      );
      await tester.pumpWidget(
        MaterialApp(
          home: CheckInView(
            api: api,
            preferences: Preferences(),
            today: {'patient_id': 'fixture', 'date': '2026-09-12'},
            item: {
              'item_id': 'item',
              'exercise_id': 'knee_extension',
              'sets': 2,
              'reps': 10,
              'completion_status': 'partial',
              'pain_before': 0,
              'pain_after': 2,
              'fatigue': 3,
              'difficulty': 2,
              'perceived_exertion': 4,
              'symptoms_changed': true,
              'patient_comment': 'Existing response',
              'symptom_flags': ['instability'],
            },
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Existing response'), findsOneWidget);
      expect(
        tester
            .widget<CheckboxListTile>(
              find.widgetWithText(CheckboxListTile, 'Instability'),
            )
            .value,
        isTrue,
      );
      await tester.ensureVisible(
        find.widgetWithText(CheckboxListTile, 'Instability'),
      );
      await tester.tap(find.widgetWithText(CheckboxListTile, 'Instability'));
      await tester.ensureVisible(
        find.widgetWithText(CheckboxListTile, 'Increased pain'),
      );
      await tester.tap(find.widgetWithText(CheckboxListTile, 'Increased pain'));
      await tester.ensureVisible(find.text('Save check-in'));
      await tester.tap(find.text('Save check-in'));
      await tester.pumpAndSettle();
      expect(saved, isNull);
      await tester.tap(
        find.widgetWithText(CheckboxListTile, 'I have read this guidance'),
      );
      await tester.tap(find.text('Save check-in'));
      await tester.pumpAndSettle();
      expect(saved?['pain_before'], 0);
      expect(saved?['pain_after'], 2);
      expect(saved?['fatigue'], 3);
      expect(saved?['symptom_flags'], ['pain_increase']);
      expect(saved?['note'], 'Existing response');
      expect(saved?['safety_acknowledged'], true);
      expect(find.text('Your check-in is saved.'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'clinician review cannot submit without rationale and attestation',
    (tester) async {
      Map<String, dynamic>? body;
      var completed = false;
      final api = ApiClient(
        'http://localhost:8020',
        MemoryTokens(),
        client: MockClient((request) async {
          body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(
            request.url.path,
            '/api/v2/therapist/patients/patient/adherence/response/acknowledge',
          );
          return http.Response('{}', 200);
        }),
      );
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: ReviewForm(
                api: api,
                preferences: Preferences(),
                patientId: 'patient',
                adherenceId: 'response',
                onSaved: () => completed = true,
              ),
            ),
          ),
        ),
      );
      await tester.tap(find.text('Mark reviewed'));
      await tester.pumpAndSettle();
      expect(body, isNull);
      await tester.enterText(
        find.byType(TextFormField),
        'Synthetic review rationale',
      );
      await tester.tap(find.text('Mark reviewed'));
      await tester.pumpAndSettle();
      expect(body, isNull);
      await tester.tap(find.byType(CheckboxListTile));
      await tester.tap(find.text('Mark reviewed'));
      await tester.pumpAndSettle();
      expect(body?['clinician_attestation'], true);
      expect(body?['disposition'], 'reviewed_no_change');
      expect(completed, true);
    },
  );
}

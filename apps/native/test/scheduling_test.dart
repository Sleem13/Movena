import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:movena_native/core/api_client.dart';
import 'package:movena_native/core/preferences.dart';
import 'package:movena_native/features/scheduling/scheduling_repository.dart';
import 'package:movena_native/features/scheduling/scheduling_view_model.dart';
import 'package:movena_native/features/scheduling/schedule_view.dart';
import 'package:movena_native/generated/models.dart';

import 'recovery_test.dart' show MemoryTokens;

const connection = {
  'assignment_id': 'one',
  'patient_id': 'p',
  'therapist_user_id': 't',
  'patient_name': 'Patient',
  'therapist_name': 'Therapist',
  'status': 'active',
};
final slot = {
  'starts_at': '2099-01-01T09:00:00Z',
  'ends_at': '2099-01-01T09:30:00Z',
};
Map<String, dynamic> appointment() => {
  'appointment_id': 'a',
  'patient_id': 'p',
  'therapist_user_id': 't',
  ...slot,
  'status': 'scheduled',
  'delivery_mode': 'video',
  'payment_status': 'pending',
  'can_join': false,
};
SchedulingRepository repository(
  Future<http.Response> Function(http.Request) handle,
) => SchedulingRepository(
  ApiClient(
    'http://localhost:8020',
    MemoryTokens(),
    client: MockClient(handle),
  ),
);

void main() {
  test(
    'booking retry retains its key; changing the request creates a fresh key',
    () async {
      final keys = <String>[];
      final repo = repository((request) async {
        keys.add(request.headers['Idempotency-Key']!);
        if (keys.length < 3) {
          return http.Response(jsonEncode({'message': 'Try again'}), 503);
        }
        return http.Response(jsonEncode(appointment()), 201);
      });
      final model = BookingViewModel(repo)
        ..choose(AppointmentSlot.fromJson(slot));
      await model.book(connection, 'video');
      expect(model.error, isNotNull);
      expect(model.selected, isNotNull);
      await model.book(connection, 'video');
      expect(keys[0], keys[1]);
      await model.book(connection, 'in_person');
      expect(keys[2], isNot(keys[1]));
      expect(model.booked!.appointmentId, 'a');
      await model.book(connection, 'in_person');
      expect(keys.length, 3);
      model.dispose();
    },
  );
  test(
    'late availability responses cannot replace the newly selected day',
    () async {
      final old = Completer<http.Response>();
      final repo = repository((request) async {
        if (request.url.queryParameters['day'] == '2099-01-01') {
          return old.future;
        }
        return http.Response(
          jsonEncode({
            'therapist_user_id': 't',
            'date': '2099-01-02',
            'slots': [],
          }),
          200,
        );
      });
      final model = BookingViewModel(repo);
      final first = model.loadSlots('t', '2099-01-01');
      await model.loadSlots('t', '2099-01-02');
      old.complete(
        http.Response(
          jsonEncode({
            'therapist_user_id': 't',
            'date': '2099-01-01',
            'slots': [slot],
          }),
          200,
        ),
      );
      await first;
      expect(model.slots, isEmpty);
      expect(model.loadingSlots, isFalse);
      model.dispose();
    },
  );
  test('video links reject expired credentials and encode valid tokens', () {
    final values = {
      'appointment_id': 'a',
      'room_url': 'https://video.example.test/room?lang=ar',
      'meeting_token': 'a+b/c==',
      'expires_at': '2099-01-01T00:00:00Z',
    };
    final uri = visitUri(AppointmentJoinResponse.fromJson(values));
    expect(uri.queryParameters['t'], 'a+b/c==');
    expect(uri.queryParameters['lang'], 'ar');
    for (final change in [
      {'expires_at': '2000-01-01T00:00:00Z'},
      {'room_url': 'http://video.example.test'},
      {'room_url': 'https://user:pass@video.example.test'},
      {'meeting_token': ''},
    ]) {
      expect(
        () =>
            visitUri(AppointmentJoinResponse.fromJson({...values, ...change})),
        throwsA(isA<ApiFailure>()),
      );
    }
  });
  testWidgets('failed cancellation retains the entered reason for retry', (
    tester,
  ) async {
    var attempts = 0;
    await tester.pumpWidget(
      MaterialApp(
        home: CancellationView(
          preferences: Preferences(),
          onSave: (reason) async {
            attempts++;
            expect(reason, 'Please move my visit');
            throw const ApiFailure('Offline');
          },
        ),
      ),
    );
    await tester.enterText(find.byType(TextFormField), 'Please move my visit');
    await tester.tap(find.widgetWithText(FilledButton, 'Cancel appointment'));
    await tester.pumpAndSettle();
    expect(attempts, 1);
    expect(find.text('Please move my visit'), findsOneWidget);
    expect(find.textContaining('Offline'), findsOneWidget);
    await tester.tap(find.widgetWithText(FilledButton, 'Cancel appointment'));
    await tester.pumpAndSettle();
    expect(attempts, 2);
  });
  testWidgets('Arabic booking fits a narrow screen with enlarged text', (
    tester,
  ) async {
    await initializeDateFormatting('ar');
    tester.view.physicalSize = const Size(320, 700);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final p = Preferences()..language = 'ar';
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('ar'),
        supportedLocales: const [Locale('en'), Locale('ar')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(context)
              .copyWith(textScaler: const TextScaler.linear(2)),
          child: child!,
        ),
        home: BookingView(
          repository: repository((_) async => http.Response('{}', 200)),
          preferences: p,
          connections: const [connection],
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    expect(
      Directionality.of(tester.element(find.byType(BookingView))),
      TextDirection.rtl,
    );
    await tester.drag(find.byType(ListView), const Offset(0, -500));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });
}

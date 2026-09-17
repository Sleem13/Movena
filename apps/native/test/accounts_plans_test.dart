import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:movena_native/core/api_client.dart';
import 'package:movena_native/core/preferences.dart';
import 'package:movena_native/core/session.dart';
import 'package:movena_native/main.dart';
import 'package:movena_native/features/auth/account_view_model.dart';
import 'package:movena_native/features/auth/account_view.dart';
import 'package:movena_native/features/auth/login_view.dart';
import 'package:movena_native/features/care/plans_view.dart';
import 'package:movena_native/features/care/plans_view_model.dart';

import 'recovery_test.dart' show MemoryTokens;

ApiClient api(Future<http.Response> Function(http.Request) handler) =>
    ApiClient(
      'http://localhost:8020',
      MemoryTokens(),
      client: MockClient(handler),
    );
void main() {
  test(
    'account deep links accept only known routes with bounded opaque tokens',
    () {
      final token = 'a' * 48;
      expect(
        AccountLink.parse(Uri.parse('movena://reset-password?token=$token'))
            ?.mode,
        'reset-password',
      );
      expect(
        AccountLink.parse(Uri.parse('movena:///verify-email?token=$token'))
            ?.token,
        token,
      );
      for (final link in [
        'https://reset-password?token=$token',
        'movena://other?token=$token',
        'movena://verify-email/path?token=$token',
        'movena://verify-email?token=short',
        'movena://user@verify-email?token=$token',
      ]) {
        expect(AccountLink.parse(Uri.parse(link)), isNull);
      }
      expect(validNewPassword('ع' * 36), isTrue);
      expect(validNewPassword('ع' * 37), isFalse);
      expect(validNewPassword('😀' * 4), isFalse);
    },
  );
  testWidgets('warm account link opens its form without submitting the token', (
    tester,
  ) async {
    var calls = 0;
    final client = api((_) async {
      calls++;
      return http.Response('{}', 200);
    });
    final session = SessionRepository(client)..loading = false;
    final stream = StreamController<Uri>();
    await tester.pumpWidget(
      MovenaApp(
        session: session,
        preferences: Preferences(),
        accountLinks: stream.stream,
      ),
    );
    stream.add(Uri.parse('movena://reset-password?token=${'a' * 48}'));
    await tester.pumpAndSettle();
    expect(find.byType(AccountFlowView), findsOneWidget);
    expect(find.widgetWithText(TextFormField, 'New password'), findsOneWidget);
    expect(calls, 0);
    await tester.pumpWidget(const SizedBox());
    unawaited(stream.close());
  });
  testWidgets(
    'account link received during restoration waits for the navigator',
    (tester) async {
      final session = SessionRepository(
        api((_) async => http.Response('{}', 200)),
      );
      final stream = StreamController<Uri>();
      await tester.pumpWidget(
        MovenaApp(
          session: session,
          preferences: Preferences(),
          accountLinks: stream.stream,
        ),
      );
      stream.add(Uri.parse('movena://verify-email?token=${'a' * 48}'));
      await tester.pump();
      expect(find.byType(AccountFlowView), findsNothing);
      await session.restore();
      await tester.pumpAndSettle();
      expect(find.byType(AccountFlowView), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
      unawaited(stream.close());
    },
  );
  testWidgets(
    'return to login from a signed-in account link clears the local session',
    (tester) async {
      final tokens = MemoryTokens()..value = 'old-session';
      final client = ApiClient(
        'http://localhost:8020',
        tokens,
        client: MockClient((_) async => http.Response('[]', 200)),
      );
      final session = SessionRepository(client)
        ..loading = false
        ..user = {
          'user_id': 'fixture',
          'role': 'support',
          'username': 'Fixture',
          'email': 'fixture@example.test',
        };
      final stream = StreamController<Uri>();
      await tester.pumpWidget(
        MovenaApp(
          session: session,
          preferences: Preferences(),
          accountLinks: stream.stream,
        ),
      );
      stream.add(Uri.parse('movena://verify-email?token=${'a' * 48}'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Return to login'));
      await tester.pumpAndSettle();
      expect(tokens.value, isNull);
      expect(session.user, isNull);
      expect(find.byType(LoginView), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
      unawaited(stream.close());
    },
  );
  test(
    'account model blocks double submit and preserves failure for retry',
    () async {
      final waiting = Completer<http.Response>();
      var calls = 0;
      final model = AccountViewModel(
        api((_) async {
          calls++;
          if (calls == 1) return waiting.future;
          return http.Response('{"message":"sent"}', 200);
        }),
      );
      final first = model.submit('forgot-password', {
        'email': 'fixture@example.test',
      });
      await model.submit('forgot-password', {'email': 'fixture@example.test'});
      waiting.complete(http.Response('{"message":"Offline"}', 503));
      await first;
      expect(calls, 1);
      expect(model.error, contains('Offline'));
      await model.submit('forgot-password', {'email': 'fixture@example.test'});
      expect(model.done, isTrue);
      expect(model.successKey, 'sent');
      model.dispose();
    },
  );
  test(
    'plan publication retry uses the same key after an uncertain response',
    () async {
      final keys = <String>[];
      final model = PlanEditorModel(
        PlansRepository(
          api((request) async {
            keys.add(request.headers['Idempotency-Key']!);
            return http.Response('{"message":"Unresolved"}', 503);
          }),
        ),
        'p',
      );
      final values = {
        'title': 'Synthetic',
        'items': [
          {
            'exercise_id': 'knee_extension',
            'sets': 2,
            'reps': 8,
            'days_per_week': 3,
          },
        ],
      };
      await model.save(values);
      await model.save(values);
      expect(keys[0], keys[1]);
      expect(model.done, isFalse);
      expect(model.error, contains('Unresolved'));
      model.dispose();
    },
  );
  testWidgets('Arabic plan editor fits narrow screens with enlarged text', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 740);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final p = Preferences()..language = 'ar';
    final repo = PlansRepository(
      api(
        (_) async => http.Response(
          jsonEncode([
            {'exercise_id': 'knee_extension'},
          ]),
          200,
        ),
      ),
    );
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('ar'),
        supportedLocales: const [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        theme: movenaTheme(Brightness.dark),
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(context)
              .copyWith(textScaler: const TextScaler.linear(2)),
          child: child!,
        ),
        home: PlanEditor(repository: repo, patientId: 'p', preferences: p),
      ),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    await tester.drag(
      find.byType(SingleChildScrollView),
      const Offset(0, -1400),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });
  testWidgets('registration starts with both consent choices unchecked', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AccountFlowView(
          api: api((_) async => http.Response('{}', 200)),
          preferences: Preferences(),
          mode: 'register',
        ),
      ),
    );
    final consent = tester.widgetList<CheckboxListTile>(
      find.byType(CheckboxListTile),
    );
    expect(consent.length, 2);
    expect(consent.every((value) => value.value == false), isTrue);
    expect(
      tester.widget<FilledButton>(find.byType(FilledButton)).onPressed,
      isNull,
    );
  });
}

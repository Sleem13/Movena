import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:movena_native/core/preferences.dart';
import 'package:movena_native/features/scheduling/visit_notes_model.dart';
import 'package:movena_native/features/scheduling/visit_notes_view.dart';

import 'patient_account_test.dart' show makeApi;

Map<String, dynamic> note(Map<String, dynamic> body) => {
  'note_id': 'n',
  'appointment_id': 'visit',
  'therapist_user_id': 't',
  'created_at': '2026-09-13T12:00:00Z',
  'updated_at': '2026-09-13T12:00:00Z',
  ...body,
};
void main() {
  test('uncertain note retry freezes payload and key then confirms only one saved note', () async {
    final writes = <http.Request>[];
    final model = VisitNotesModel(
      VisitNotesRepository(
        makeApi((request) async {
          if (request.method == 'GET') return http.Response('[]', 200);
          writes.add(request);
          return writes.length == 1
              ? http.Response('{"message":"Offline"}', 503)
              : http.Response(jsonEncode(note(jsonDecode(request.body))), 201);
        }),
      ),
      'visit',
      true,
    );
    expect(await model.save(' Original ', ' ', false), isFalse);
    expect(model.uncertain, isTrue);
    expect(
      await model.save('Changed after ambiguous failure', 'Changed', true),
      isTrue,
    );
    expect(writes[0].body, writes[1].body);
    expect(
      writes[0].headers['Idempotency-Key'],
      writes[1].headers['Idempotency-Key'],
    );
    expect(jsonDecode(writes[1].body)['patient_visible'], isFalse);
    expect(jsonDecode(writes[1].body)['recommendations'], isNull);
    expect(model.saved, isTrue);
    model.dispose();
  });
  test(
    'patient notes use the patient reader and cannot submit a staff note',
    () async {
      var calls = 0;
      final model = VisitNotesModel(
        VisitNotesRepository(
          makeApi((request) async {
            calls++;
            expect(request.method, 'GET');
            expect(
              request.url.path,
              '/api/v2/patient/appointments/visit/session-notes',
            );
            return http.Response(
              jsonEncode([
                note({'summary': 'Shared', 'patient_visible': true}),
              ]),
              200,
            );
          }),
        ),
        'visit',
        false,
      );
      await model.load();
      expect(model.notes.single.summary, 'Shared');
      expect(await model.save('Forbidden', '', true), isFalse);
      expect(calls, 1);
      model.dispose();
    },
  );
  testWidgets(
    'Arabic note editor defaults private and fits enlarged text on a phone',
    (tester) async {
      tester.view.physicalSize = const Size(320, 740);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final p = Preferences()..language = 'ar';
      final api = makeApi((request) async => http.Response('[]', 200));
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
          home: VisitNotesView(
            api: api,
            preferences: p,
            appointmentId: 'visit',
            appointmentTime: '١٣ سبتمبر ٢٠٢٦، ٣:٠٠ م',
            participant: 'مريض تجريبي',
            staff: true,
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('مريض تجريبي'), findsOneWidget);
      await tester.ensureVisible(find.text(p.t('addVisitNote')));
      await tester.tap(find.text(p.t('addVisitNote')));
      await tester.pumpAndSettle();
      expect(
        tester.widget<CheckboxListTile>(find.byType(CheckboxListTile)).value,
        isFalse,
      );
      await tester.enterText(
        find.byType(TextFormField).first,
        'ملاحظة تجريبية للتحقق فقط',
      );
      await tester.drag(
        find.byType(SingleChildScrollView),
        const Offset(0, -1500),
      );
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    },
  );
}

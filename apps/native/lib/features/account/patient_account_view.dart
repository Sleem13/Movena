import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';
import '../../generated/client.dart';
import '../../generated/models.dart';
import 'patient_account_model.dart';
import '../care/today_view.dart';
import '../care/care_view.dart';
import '../scheduling/schedule_view.dart';

String accountDate(String? value, Preferences p) {
  if (value == null) return '—';
  final normalized = RegExp(r'(Z|[+-]\d\d:\d\d)$').hasMatch(value)
      ? value
      : '${value}Z';
  final date = DateTime.tryParse(normalized);
  return date == null
      ? '—'
      : DateFormat.yMMMd(p.language).format(date.toLocal());
}

class HealthProfileView extends StatelessWidget {
  final ApiClient api;
  final Preferences preferences;
  const HealthProfileView({
    super.key,
    required this.api,
    required this.preferences,
  });
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(preferences.t('healthProfile'))),
    body: SafeArea(
      child: ResourceView(
        api: api,
        path: 'patient/health-profile',
        preferences: preferences,
        builder: (data, _) => HealthProfileForm(
          api: api,
          preferences: preferences,
          initial: objectOf(data),
        ),
      ),
    ),
  );
}

class HealthProfileForm extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final Map<String, dynamic> initial;
  const HealthProfileForm({
    super.key,
    required this.api,
    required this.preferences,
    required this.initial,
  });
  @override
  State<HealthProfileForm> createState() => _HealthProfileFormState();
}

class _HealthProfileFormState extends State<HealthProfileForm> {
  late final HealthProfileModel model;
  late final Map<String, TextEditingController> fields;
  final form = GlobalKey<FormState>();
  @override
  void initState() {
    super.initState();
    model = HealthProfileModel(PatientAccountRepository(widget.api));
    fields = {
      for (final field in healthFields)
        field.$1: TextEditingController(
          text: widget.initial[field.$1] as String?,
        ),
    };
  }

  @override
  void dispose() {
    for (final field in fields.values) {
      field.dispose();
    }
    model.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return ListenableBuilder(
      listenable: model,
      builder: (context, _) => SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Panel(
              child: Form(
                key: form,
                onChanged: model.changed,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(p.t('healthIntro')),
                    const SizedBox(height: 20),
                    for (final field in healthFields)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: TextFormField(
                          controller: fields[field.$1],
                          enabled: !model.busy,
                          maxLength: field.$3,
                          maxLines: field.$3 > 120 ? 5 : 1,
                          keyboardType: field.$1.endsWith('phone')
                              ? TextInputType.phone
                              : field.$3 > 120
                              ? TextInputType.multiline
                              : TextInputType.text,
                          decoration: InputDecoration(labelText: p.t(field.$2)),
                          validator: (v) => (v ?? '').length > field.$3
                              ? p.t('invalidInput')
                              : null,
                        ),
                      ),
                    if (model.error != null)
                      Semantics(liveRegion: true, child: Text(model.error!)),
                    if (model.saved)
                      Semantics(liveRegion: true, child: Text(p.t('changesSaved'))),
                    FilledButton(
                      onPressed: model.busy
                          ? null
                          : () {
                              if (form.currentState!.validate()) {
                                model.save({
                                  for (final entry in fields.entries)
                                    entry.key: entry.value.text,
                                });
                              }
                            },
                      child: Text(p.t(model.busy ? 'loading' : 'saveChanges')),
                    ),
                  ],
                ),
              ),
            ),
            Panel(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    p.t('consentHistory'),
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  ResourceView(
                    api: widget.api,
                    path: 'patient/consents',
                    preferences: p,
                    builder: (data, _) {
                      final rows = rowsOf(data);
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          if (rows.isEmpty) Text(p.t('noConsents')),
                          for (final row in rows) ...[
                            const Divider(),
                            Text(
                              [
                                    'privacy',
                                    'terms',
                                    'care_data',
                                    'media_upload',
                                  ].contains(row['consent_type'])
                                  ? p.t('consent_${row['consent_type']}')
                                  : row['consent_type'].toString(),
                            ),
                            Text(
                              '${p.t(row['accepted'] == true ? 'consentAccepted' : 'consentDeclined')} · ${p.t('consentVersion')} ${row['version']}',
                            ),
                            Text(accountDate(row['accepted_at'] as String?, p)),
                          ],
                        ],
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class NotificationsView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  const NotificationsView({
    super.key,
    required this.api,
    required this.preferences,
  });
  @override
  State<NotificationsView> createState() => _NotificationsViewState();
}

class _NotificationsViewState extends State<NotificationsView> {
  String? busy, error;
  final readIds = <String>{};
  void open(String value) {
    final api = widget.api, p = widget.preferences;
    final Widget screen = switch (value) {
      'schedule' => ScheduleView(api: api, preferences: p, role: 'patient'),
      'care' => CareView(api: api, preferences: p),
      _ => TodayView(api: api, preferences: p),
    };
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => Scaffold(
          appBar: AppBar(title: Text(p.t(value))),
          body: SafeArea(child: screen),
        ),
      ),
    );
  }

  Future<void> read(String id) async {
    if (busy != null) return;
    setState(() {
      busy = id;
      error = null;
    });
    try {
      await CoreApi(widget.api.request).readNotification(id);
      if (mounted) setState(() => readIds.add(id));
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => busy = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return Scaffold(
      appBar: AppBar(title: Text(p.t('notifications'))),
      body: SafeArea(
        child: ResourceView(
          api: widget.api,
          path: 'patient/notifications',
          preferences: p,
          builder: (data, refresh) {
            final rows = rowsOf(data)
                .map(NotificationSummary.fromJson)
                .toList();
            return RefreshIndicator(
              onRefresh: () async => refresh(),
              child: ListView(
                padding: const EdgeInsets.all(20),
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  if (error != null)
                    Semantics(liveRegion: true, child: Text(error!)),
                  if (rows.isEmpty) Panel(child: Text(p.t('noNotifications'))),
                  for (final row in rows)
                    Panel(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            p.t(
                              row.readAt == null &&
                                      !readIds.contains(row.notificationId)
                                  ? 'unread'
                                  : 'read',
                            ),
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.secondary,
                            ),
                          ),
                          Text(
                            row.title,
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          const SizedBox(height: 12),
                          Text(row.body),
                          const SizedBox(height: 12),
                          Text(accountDate(row.createdAt, p)),
                          if (notificationDestination(row.actionUrl) != null)
                            OutlinedButton(
                              onPressed: () =>
                                  open(notificationDestination(row.actionUrl)!),
                              child: Text(p.t('openNotification')),
                            ),
                          if (row.readAt == null &&
                              !readIds.contains(row.notificationId))
                            OutlinedButton(
                              onPressed: busy != null
                                  ? null
                                  : () => read(row.notificationId),
                              child: Text(
                                p.t(
                                  busy == row.notificationId
                                      ? 'loading'
                                      : 'markRead',
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  if (rows.length >= 100) Text(p.t('inboxLimit')),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import 'review_form.dart';
import 'plans_view.dart';
import 'progress_reports_view.dart';
import '../scheduling/schedule_view.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';

class CareView extends StatelessWidget {
  final ApiClient api;
  final Preferences preferences;
  const CareView({super.key, required this.api, required this.preferences});
  @override
  Widget build(BuildContext context) => ResourceView(
    api: api,
    path: 'connections',
    preferences: preferences,
    builder: (data, refreshConnections) {
      final connections = rowsOf(data);
      final p = preferences;
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            p.t('careTeam'),
            style: Theme.of(context).textTheme.headlineLarge,
          ),
          const SizedBox(height: 24),
          OutlinedButton(
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => Scaffold(
                  appBar: AppBar(title: Text(p.t('appointments'))),
                  body: SafeArea(
                    child: ScheduleView(
                      api: api,
                      preferences: p,
                      role: 'patient',
                    ),
                  ),
                ),
              ),
            ),
            child: Text(p.t('viewSchedule')),
          ),
          if (connections.isEmpty) Panel(child: Text(p.t('noConnections'))),
          for (final row in connections)
            Card(
              child: ListTile(
                leading: const Icon(Icons.person_outline),
                title: Text(row['therapist_name']),
                subtitle: Text(row['status']),
              ),
            ),
          const SizedBox(height: 28),
          Text(
            p.t('invitations'),
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 16),
          ResourceView(
            api: api,
            path: 'care-invitations',
            preferences: p,
            builder: (value, refreshInvitations) {
              final invitations = rowsOf(value)
                  .where((i) => i['status'] == 'pending')
                  .toList();
              return Column(
                children: [
                  if (invitations.isEmpty) Text(p.t('noInvitations')),
                  for (final row in invitations)
                    _Invitation(
                      api: api,
                      preferences: p,
                      row: row,
                      onChanged: () {
                        refreshConnections();
                        refreshInvitations();
                      },
                    ),
                ],
              );
            },
          ),
        ],
      );
    },
  );
}

class _Invitation extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final Map<String, dynamic> row;
  final VoidCallback onChanged;
  const _Invitation({
    required this.api,
    required this.preferences,
    required this.row,
    required this.onChanged,
  });
  @override
  State<_Invitation> createState() => _InvitationState();
}

class _InvitationState extends State<_Invitation> {
  bool busy = false;
  String? error;
  Future<void> respond(String action) async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await widget.api.request(
        'care-invitations/${Uri.encodeComponent(widget.row['invitation_id'])}/respond',
        method: 'POST',
        body: {'action': action},
      );
      widget.onChanged();
    } catch (e) {
      if (mounted) {
        setState(() {
          error = e.toString();
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          busy = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => Panel(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          widget.row['therapist_name'],
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        FilledButton(
          onPressed: busy ? null : () => respond('accept'),
          child: Text(widget.preferences.t('accept')),
        ),
        const SizedBox(height: 12),
        OutlinedButton(
          onPressed: busy ? null : () => respond('decline'),
          child: Text(widget.preferences.t('decline')),
        ),
        if (error != null) Text(error!),
      ],
    ),
  );
}

class PatientsView extends StatelessWidget {
  final ApiClient api;
  final Preferences preferences;
  const PatientsView({super.key, required this.api, required this.preferences});
  @override
  Widget build(BuildContext context) => ResourceView(
    api: api,
    path: 'therapist/patients',
    preferences: preferences,
    builder: (data, refresh) {
      final rows = rowsOf(data);
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            preferences.t('patients'),
            style: Theme.of(context).textTheme.headlineLarge,
          ),
          const SizedBox(height: 24),
          if (rows.isEmpty) Text(preferences.t('noPatients')),
          for (final row in rows)
            Card(
              child: ListTile(
                minTileHeight: 80,
                leading: const Icon(Icons.person_outline),
                title: Text(row['display_name']),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => PatientReviewView(
                      api: api,
                      preferences: preferences,
                      patient: row,
                    ),
                  ),
                ),
              ),
            ),
        ],
      );
    },
  );
}

class PatientReviewView extends StatelessWidget {
  final ApiClient api;
  final Preferences preferences;
  final Map<String, dynamic> patient;
  const PatientReviewView({
    super.key,
    required this.api,
    required this.preferences,
    required this.patient,
  });
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(patient['display_name'])),
    body: ResourceView(
      api: api,
      path:
          'therapist/patients/${Uri.encodeComponent(patient['patient_id'])}/adherence',
      preferences: preferences,
      builder: (data, refresh) {
        final rows = rowsOf(data);
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            if (rows.isEmpty) Text(preferences.t('noResponses')),
            OutlinedButton(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => PlansView(
                    api: api,
                    preferences: preferences,
                    patientId: patient['patient_id'],
                  ),
                ),
              ),
              child: Text(preferences.t('carePlans')),
            ),
            OutlinedButton(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => CreateProgressReportView(
                    api: api,
                    preferences: preferences,
                    patientId: patient['patient_id'],
                  ),
                ),
              ),
              child: Text(preferences.t('createProgressReport')),
            ),
            for (final row in rows)
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Panel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        preferences.date(row['scheduled_date']),
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      Text(
                        preferences.t(
                          row['completion_status'] == 'completed'
                              ? 'complete'
                              : row['completion_status'] == 'partial'
                              ? 'partial'
                              : 'missed',
                        ),
                      ),
                      Text(
                        '${preferences.t('painBefore')}: ${row['pain_before'] ?? preferences.t('unavailable')}',
                      ),
                      Text(
                        '${preferences.t('painAfter')}: ${row['pain_after'] ?? preferences.t('unavailable')}',
                      ),
                      if (row['note'] != null) Text(row['note']),
                      if (row['supportive_instruction'] != null)
                        Text(row['supportive_instruction']),
                      const SizedBox(height: 16),
                      if (row['clinician_review_required'] == true &&
                          row['reviewed_at'] == null)
                        ReviewForm(
                          key: ValueKey(row['adherence_id']),
                          api: api,
                          preferences: preferences,
                          patientId: patient['patient_id'],
                          adherenceId: row['adherence_id'],
                          onSaved: refresh,
                        )
                      else
                        Text(
                          preferences.t(
                            row['reviewed_at'] != null
                                ? 'reviewSaved'
                                : 'noReviewRequired',
                          ),
                        ),
                    ],
                  ),
                ),
              ),
          ],
        );
      },
    ),
  );
}

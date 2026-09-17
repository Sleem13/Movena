import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/preferences.dart';
import '../../core/session.dart';
import '../../core/resource_view.dart';
import '../care/today_view.dart';
import '../care/care_view.dart';
import '../analysis/analyze_view.dart';
import '../care/progress_view.dart';
import '../scheduling/schedule_view.dart';
import '../account/patient_account_view.dart';
import '../account/data_rights_view.dart';

class Workspace extends StatefulWidget {
  final SessionRepository session;
  final Preferences preferences;
  const Workspace({
    super.key,
    required this.session,
    required this.preferences,
  });
  @override
  State<Workspace> createState() => _WorkspaceState();
}

class _WorkspaceState extends State<Workspace> {
  int selected = 0;
  @override
  Widget build(BuildContext context) {
    final role = widget.session.user!['role'];
    final p = widget.preferences;
    final api = widget.session.api;
    final List<(String, IconData)> tabs = switch (role) {
      'patient' => [
        ('today', Icons.home_outlined),
        ('progress', Icons.show_chart),
        ('care', Icons.people_outline),
        ('account', Icons.person_outline),
      ],
      'therapist' => [
        ('patients', Icons.people_outline),
        ('review', Icons.fact_check_outlined),
        ('schedule', Icons.calendar_month_outlined),
        ('account', Icons.person_outline),
      ],
      'admin' || 'super_admin' => [
        ('overview', Icons.dashboard_outlined),
        ('people', Icons.people_outline),
        ('operations', Icons.tune),
        ('account', Icons.person_outline),
      ],
      _ => [('account', Icons.person_outline)],
    };
    if (selected >= tabs.length) selected = 0;
    final current = tabs[selected].$1;
    final body = switch (current) {
      'today' => TodayView(api: api, preferences: p),
      'progress' => ProgressView(api: api, preferences: p),
      'care' => CareView(api: api, preferences: p),
      'patients' || 'review' => PatientsView(api: api, preferences: p),
      'schedule' => ScheduleView(api: api, preferences: p, role: role),
      'operations' => Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(24),
            child: OutlinedButton.icon(
              icon: const Icon(Icons.calendar_month),
              label: Text(p.t('appointments')),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => Scaffold(
                    appBar: AppBar(title: Text(p.t('appointments'))),
                    body: SafeArea(
                      child: ScheduleView(api: api, preferences: p, role: role),
                    ),
                  ),
                ),
              ),
            ),
          ),
          if (role == 'super_admin')
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: OutlinedButton.icon(
                icon: const Icon(Icons.policy_outlined),
                label: Text(p.t('dataRightsQueue')),
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        AdminDataRightsView(api: api, preferences: p),
                  ),
                ),
              ),
            ),
          Expanded(
            child: MigrationView(section: current, preferences: p),
          ),
        ],
      ),
      'account' => AccountView(session: widget.session, preferences: p),
      _ => MigrationView(section: current, preferences: p),
    };
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Movena',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        actions: [
          IconButton(
            tooltip: p.t('account'),
            onPressed: () => setState(() {
              selected = tabs.length - 1;
            }),
            icon: const Icon(Icons.account_circle_outlined),
          ),
        ],
      ),
      body: SafeArea(child: body),
      bottomNavigationBar: tabs.length < 2
          ? null
          : NavigationBar(
              selectedIndex: selected,
              onDestinationSelected: (value) => setState(() {
                selected = value;
              }),
              destinations: tabs
                  .map(
                    (tab) => NavigationDestination(
                      icon: Icon(tab.$2),
                      label: p.t(tab.$1),
                    ),
                  )
                  .toList(),
            ),
    );
  }
}

class AccountView extends StatelessWidget {
  final SessionRepository session;
  final Preferences preferences;
  const AccountView({
    super.key,
    required this.session,
    required this.preferences,
  });
  @override
  Widget build(BuildContext context) {
    final p = preferences;
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Text(p.t('account'), style: Theme.of(context).textTheme.headlineLarge),
        const SizedBox(height: 24),
        Panel(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                session.user!['full_name'] ?? session.user!['email'],
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 24),
              if (session.user!['role'] == 'patient') ...[
                OutlinedButton(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) =>
                          HealthProfileView(api: session.api, preferences: p),
                    ),
                  ),
                  child: Text(p.t('healthProfile')),
                ),
                OutlinedButton(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) =>
                          NotificationsView(api: session.api, preferences: p),
                    ),
                  ),
                  child: Text(p.t('notifications')),
                ),
                OutlinedButton(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => PatientDataRightsView(
                        api: session.api,
                        preferences: p,
                      ),
                    ),
                  ),
                  child: Text(p.t('dataRights')),
                ),
              ],
              DropdownButtonFormField<ThemeMode>(
                initialValue: p.themeMode,
                decoration: InputDecoration(labelText: p.t('theme')),
                items: ThemeMode.values
                    .map(
                      (v) =>
                          DropdownMenuItem(value: v, child: Text(p.t(v.name))),
                    )
                    .toList(),
                onChanged: (v) => v == null ? null : p.setTheme(v),
              ),
              const SizedBox(height: 20),
              DropdownButtonFormField<String>(
                initialValue: p.language,
                decoration: InputDecoration(labelText: p.t('language')),
                items: const [
                  DropdownMenuItem(value: 'en', child: Text('English')),
                  DropdownMenuItem(value: 'ar', child: Text('العربية')),
                ],
                onChanged: (v) => v == null ? null : p.setLanguage(v),
              ),
              const SizedBox(height: 24),
              if ([
                'patient',
                'therapist',
                'admin',
                'super_admin',
              ].contains(session.user!['role']))
                OutlinedButton(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => Scaffold(
                        appBar: AppBar(title: Text(p.t('appointments'))),
                        body: SafeArea(
                          child: ScheduleView(
                            api: session.api,
                            preferences: p,
                            role: session.user!['role'],
                          ),
                        ),
                      ),
                    ),
                  ),
                  child: Text(p.t('viewSchedule')),
                ),
              if (session.user!['role'] != 'support')
                OutlinedButton(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) =>
                          AnalyzeView(api: session.api, preferences: p),
                    ),
                  ),
                  child: Text(p.t('analyze')),
                ),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: () async {
                  try {
                    await session.logout();
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context)
                          .showSnackBar(SnackBar(content: Text(e.toString())));
                    }
                  }
                },
                child: Text(p.t('logout')),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        Text(p.t('analysisDisclaimer')),
      ],
    );
  }
}

class MigrationView extends StatelessWidget {
  final String section;
  final Preferences preferences;
  const MigrationView({
    super.key,
    required this.section,
    required this.preferences,
  });
  @override
  Widget build(BuildContext context) => ListView(
    padding: const EdgeInsets.all(24),
    children: [
      Text(
        preferences.t(section),
        style: Theme.of(context).textTheme.headlineLarge,
      ),
      const SizedBox(height: 24),
      Panel(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(preferences.t('readonly')),
            const SizedBox(height: 20),
            OutlinedButton(
              onPressed: () async {
                const origin = String.fromEnvironment('MOVENA_LEGACY_WEB_URL');
                final uri = Uri.tryParse(origin);
                if (uri == null || uri.scheme != 'https' || uri.host.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(preferences.t('unavailable'))),
                  );
                  return;
                }
                final path = section == 'schedule' || section == 'review'
                    ? '/therapist'
                    : '/admin/workflow';
                if (!await launchUrl(
                      uri.resolve(path),
                      mode: LaunchMode.externalApplication,
                    ) &&
                    context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(preferences.t('unavailable'))),
                  );
                }
              },
              child: Text(preferences.t('openExisting')),
            ),
          ],
        ),
      ),
    ],
  );
}

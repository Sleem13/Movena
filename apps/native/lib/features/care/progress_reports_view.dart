import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';

Uri? reportUri(ApiClient api, String? value) {
  if (value == null || value.isEmpty) return null;
  final parsed = Uri.tryParse(value);
  if (parsed == null) return null;
  final resolved = parsed.hasScheme
      ? parsed
      : value.startsWith('/api/v1/')
      ? api.origin.resolve('/api/v2/${value.substring('/api/v1/'.length)}')
      : api.origin.resolveUri(parsed);
  if (!{'http', 'https'}.contains(resolved.scheme) ||
      resolved.host.isEmpty ||
      resolved.userInfo.isNotEmpty) {
    return null;
  }
  return resolved;
}

class PatientReportsPanel extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  const PatientReportsPanel({
    super.key,
    required this.api,
    required this.preferences,
  });

  @override
  State<PatientReportsPanel> createState() => _PatientReportsPanelState();
}

class _PatientReportsPanelState extends State<PatientReportsPanel> {
  String? error;

  Future<void> open(String? value) async {
    final uri = reportUri(widget.api, value);
    if (uri == null ||
        !await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (mounted) setState(() => error = widget.preferences.t('accountError'));
    }
  }

  @override
  Widget build(BuildContext context) => ResourceView(
    api: widget.api,
    path: 'patient/reports',
    preferences: widget.preferences,
    builder: (value, refresh) {
      final rows = rowsOf(value);
      final p = widget.preferences;
      return Panel(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              p.t('progressReports'),
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            if (rows.isEmpty) Text(p.t('noProgressReports')),
            for (final row in rows)
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: Text(p.t('reportPeriod')),
                subtitle: Text(
                  '${p.date(row['period_start'])} · ${p.date(row['period_end'])}',
                ),
                trailing: const Icon(Icons.open_in_new),
                onTap: () => open(row['download_url']?.toString()),
              ),
            if (error != null) Semantics(liveRegion: true, child: Text(error!)),
            OutlinedButton(onPressed: refresh, child: Text(p.t('refresh'))),
          ],
        ),
      );
    },
  );
}

class CreateProgressReportView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final String patientId;
  const CreateProgressReportView({
    super.key,
    required this.api,
    required this.preferences,
    required this.patientId,
  });

  @override
  State<CreateProgressReportView> createState() =>
      _CreateProgressReportViewState();
}

class _CreateProgressReportViewState extends State<CreateProgressReportView> {
  late DateTime start;
  late DateTime end;
  bool share = false;
  bool busy = false;
  String? error;
  String? downloadUrl;

  @override
  void initState() {
    super.initState();
    end = DateUtils.dateOnly(DateTime.now());
    start = end.subtract(const Duration(days: 29));
  }

  String day(DateTime value) =>
      '${value.year.toString().padLeft(4, '0')}-${value.month.toString().padLeft(2, '0')}-${value.day.toString().padLeft(2, '0')}';

  Future<void> choose(bool first) async {
    final current = first ? start : end;
    final result = await showDatePicker(
      context: context,
      initialDate: current,
      firstDate: DateTime(2000),
      lastDate: DateTime.now().add(const Duration(days: 366)),
    );
    if (result != null) setState(() => first ? start = result : end = result);
  }

  Future<void> submit() async {
    final span = end.difference(start).inDays;
    if (span < 0 || span > 366) {
      setState(() => error = widget.preferences.t('invalidReportPeriod'));
      return;
    }
    setState(() {
      busy = true;
      error = null;
      downloadUrl = null;
    });
    try {
      final query = Uri(
        queryParameters: {
          'period_start': day(start),
          'period_end': day(end),
          'share_with_patient': share.toString(),
        },
      ).query;
      final result = objectOf(
        await widget.api.request(
          'therapist/patients/${Uri.encodeComponent(widget.patientId)}/reports?$query',
          method: 'POST',
        ),
      );
      if (mounted) {
        setState(() => downloadUrl = result['download_url']?.toString());
      }
    } catch (reason) {
      if (mounted) setState(() => error = reason.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> open() async {
    final uri = reportUri(widget.api, downloadUrl);
    if (uri == null ||
        !await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (mounted) setState(() => error = widget.preferences.t('accountError'));
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return Scaffold(
      appBar: AppBar(title: Text(p.t('createProgressReport'))),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            Panel(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  OutlinedButton(
                    onPressed: busy ? null : () => choose(true),
                    child: Text('${p.t('reportStart')}: ${p.date(day(start))}'),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton(
                    onPressed: busy ? null : () => choose(false),
                    child: Text('${p.t('reportEnd')}: ${p.date(day(end))}'),
                  ),
                  CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    value: share,
                    onChanged: busy
                        ? null
                        : (value) => setState(() => share = value ?? false),
                    title: Text(p.t('shareReport')),
                    controlAffinity: ListTileControlAffinity.leading,
                  ),
                  FilledButton(
                    onPressed: busy ? null : submit,
                    child: Text(p.t(busy ? 'loading' : 'createProgressReport')),
                  ),
                  if (error != null)
                    Semantics(liveRegion: true, child: Text(error!)),
                  if (downloadUrl != null) ...[
                    const SizedBox(height: 12),
                    Semantics(
                      liveRegion: true,
                      child: Text(p.t('reportCreated')),
                    ),
                    OutlinedButton.icon(
                      onPressed: open,
                      icon: const Icon(Icons.open_in_new),
                      label: Text(p.t('downloadReport')),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

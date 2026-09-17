import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';
import 'data_rights_model.dart';

class PatientDataRightsView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  const PatientDataRightsView({
    super.key,
    required this.api,
    required this.preferences,
  });
  @override
  State<PatientDataRightsView> createState() => _PatientDataRightsViewState();
}

class _PatientDataRightsViewState extends State<PatientDataRightsView> {
  String type = 'export', details = '', message = '', key = newDataRightsKey();
  bool saving = false;
  late final repo = DataRightsRepository(widget.api);
  final detailsController = TextEditingController();
  @override
  void dispose() {
    detailsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(widget.preferences.t('dataRights'))),
    body: ResourceView(
      api: widget.api,
      path: 'patient/data-rights-requests',
      preferences: widget.preferences,
      builder: (data, refresh) => ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Panel(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  widget.preferences.t('dataRightsNew'),
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(widget.preferences.t('dataRightsIntro')),
                const SizedBox(height: 20),
                DropdownButtonFormField<String>(
                  initialValue: type,
                  decoration: InputDecoration(
                    labelText: widget.preferences.t('requestType'),
                  ),
                  items: ['export', 'correction', 'deletion']
                      .map(
                        (v) => DropdownMenuItem(
                          value: v,
                          child: Text(
                            widget.preferences.t('dataRightsType_$v'),
                          ),
                        ),
                      )
                      .toList(),
                  onChanged: (v) => setState(() => type = v!),
                ),
                if (type == 'deletion')
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    child: Text(widget.preferences.t('deletionWarning')),
                  ),
                TextFormField(
                  controller: detailsController,
                  maxLines: 5,
                  maxLength: 2001,
                  decoration: InputDecoration(
                    labelText: widget.preferences.t('detailsOptional'),
                  ),
                  onChanged: (v) => details = v,
                ),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: saving
                      ? null
                      : () async {
                          if (!validDataRightsDetails(details)) {
                            setState(
                              () => message = widget.preferences.t(
                                'dataRightsTooLong',
                              ),
                            );
                            return;
                          }
                          setState(() => saving = true);
                          try {
                            await repo.create(type, details, key);
                            key = newDataRightsKey();
                            details = '';
                            detailsController.clear();
                            message = widget.preferences.t(
                              'dataRightsSubmitted',
                            );
                            refresh();
                          } catch (e) {
                            message = e.toString();
                          } finally {
                            if (mounted) setState(() => saving = false);
                          }
                        },
                  child: Text(widget.preferences.t('submitRequest')),
                ),
                if (message.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Semantics(liveRegion: true, child: Text(message)),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          Text(
            widget.preferences.t('requestHistory'),
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 12),
          ...rowsOf(data).map(
            (row) => DataRightsCard(row: row, preferences: widget.preferences),
          ),
          if (rowsOf(data).isEmpty)
            Text(widget.preferences.t('noDataRightsRequests')),
        ],
      ),
    ),
  );
}

class DataRightsCard extends StatelessWidget {
  final Map<String, dynamic> row;
  final Preferences preferences;
  const DataRightsCard({
    super.key,
    required this.row,
    required this.preferences,
  });
  @override
  Widget build(BuildContext context) {
    final date = DateTime.tryParse(row['created_at']?.toString() ?? '');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    preferences.t('dataRightsType_${row['request_type']}'),
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Chip(
                  label: Text(
                    preferences.t('dataRightsStatus_${row['status']}'),
                  ),
                ),
              ],
            ),
            if (row['account_name'] != null)
              Text('${row['account_name']}\n${row['account_email'] ?? ''}'),
            if (row['details'] != null)
              Padding(
                padding: const EdgeInsets.only(top: 10),
                child: Text(row['details'].toString()),
              ),
            if (date != null)
              Padding(
                padding: const EdgeInsets.only(top: 10),
                child: Text(
                  MaterialLocalizations.of(context)
                      .formatMediumDate(date.toLocal()),
                ),
              ),
            if (row['retention_until'] != null)
              Text(
                '${preferences.t('retentionUntil')}: ${row['retention_until']}',
              ),
          ],
        ),
      ),
    );
  }
}

class AdminDataRightsView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  const AdminDataRightsView({
    super.key,
    required this.api,
    required this.preferences,
  });
  @override
  State<AdminDataRightsView> createState() => _AdminDataRightsViewState();
}

class _AdminDataRightsViewState extends State<AdminDataRightsView> {
  final reasons = <String, String>{};
  String message = '';
  late final repo = DataRightsRepository(widget.api);
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(widget.preferences.t('dataRightsQueue'))),
    body: ResourceView(
      api: widget.api,
      path: 'admin/platform/data-rights-requests',
      preferences: widget.preferences,
      builder: (data, refresh) {
        final rows = rowsOf(data);
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            Text(widget.preferences.t('dataRightsAdminIntro')),
            if (message.isNotEmpty)
              Semantics(liveRegion: true, child: Text(message)),
            const SizedBox(height: 16),
            if (rows.isEmpty)
              Text(widget.preferences.t('noDataRightsRequests')),
            ...rows.map(
              (row) => Column(
                children: [
                  DataRightsCard(row: row, preferences: widget.preferences),
                  if (row['status'] == 'pending')
                    Panel(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          TextFormField(
                            maxLines: 3,
                            maxLength: 2000,
                            decoration: InputDecoration(
                              labelText: widget.preferences.t('reviewReason'),
                            ),
                            onChanged: (value) =>
                                reasons[row['request_id'].toString()] = value,
                          ),
                          Wrap(
                            spacing: 12,
                            children: ['approve', 'reject']
                                .map(
                                  (decision) => OutlinedButton(
                                    onPressed: () =>
                                        _review(row, decision, refresh),
                                    child: Text(widget.preferences.t(decision)),
                                  ),
                                )
                                .toList(),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ],
        );
      },
    ),
  );

  Future<void> _review(
    Map<String, dynamic> row,
    String decision,
    VoidCallback refresh,
  ) async {
    final reason = reasons[row['request_id']]?.trim() ?? '';
    if (reason.length < 3) {
      setState(() => message = widget.preferences.t('reviewReasonRequired'));
      return;
    }
    try {
      await repo.review(row['request_id'].toString(), decision, reason);
      message = widget.preferences.t('reviewSaved');
      refresh();
    } catch (error) {
      message = error.toString();
    }
    if (mounted) setState(() {});
  }
}

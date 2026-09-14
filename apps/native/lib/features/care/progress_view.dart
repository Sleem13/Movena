import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';
import '../analysis/analyze_view.dart';
import 'history_view_model.dart';
import 'progress_reports_view.dart';

class ProgressView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  const ProgressView({super.key, required this.api, required this.preferences});
  @override
  State<ProgressView> createState() => _ProgressViewState();
}

class _ProgressViewState extends State<ProgressView> {
  late final HistoryViewModel model;
  @override
  void initState() {
    super.initState();
    model = HistoryViewModel(HistoryRepository(widget.api))..load();
  }

  @override
  void dispose() {
    model.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: model,
    builder: (context, _) {
      final p = widget.preferences;
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            p.t('historyTitle'),
            style: Theme.of(context).textTheme.headlineLarge,
          ),
          const SizedBox(height: 24),
          DropdownButtonFormField<String>(
            key: ValueKey(model.status),
            initialValue: model.status,
            isExpanded: true,
            decoration: InputDecoration(labelText: p.t('historyOutcome')),
            items: historyStatuses
                .map(
                  (s) => DropdownMenuItem(
                    value: s,
                    child: Text(
                      p.t(s.isEmpty ? 'historyAll' : historyStatusKey(s)),
                    ),
                  ),
                )
                .toList(),
            onChanged: (s) {
              if (s != null) model.filter(s);
            },
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              OutlinedButton(
                onPressed: model.offset == 0 ? null : model.newer,
                child: Text(p.t('historyNewer')),
              ),
              OutlinedButton(
                onPressed: model.hasOlder ? model.older : null,
                child: Text(p.t('historyOlder')),
              ),
              OutlinedButton(
                onPressed: model.busy ? null : model.load,
                child: Text(p.t('historyRefresh')),
              ),
            ],
          ),
          const SizedBox(height: 24),
          if (model.busy)
            Center(
              child: Semantics(
                label: p.t('loading'),
                child: const CircularProgressIndicator(),
              ),
            ),
          if (model.error != null)
            Panel(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Semantics(liveRegion: true, child: Text(model.error!)),
                  OutlinedButton(
                    onPressed: model.load,
                    child: Text(p.t('retry')),
                  ),
                ],
              ),
            ),
          if (model.data != null) ...[
            Semantics(
              liveRegion: true,
              child: Text(
                '${p.t('historyRecords')}: ${p.number(model.data!.total)}',
              ),
            ),
            const SizedBox(height: 12),
            if (model.data!.items.isEmpty)
              Panel(
                child: Text(
                  p.t(
                    model.status.isNotEmpty || model.offset > 0
                        ? 'historyNoMatches'
                        : 'noSessions',
                  ),
                ),
              ),
            for (final row in model.data!.items)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Card(
                  child: InkWell(
                    borderRadius: BorderRadius.circular(18),
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => Scaffold(
                          appBar: AppBar(title: Text(p.t('results'))),
                          body: ResourceView(
                            api: widget.api,
                            path:
                                'sessions/${Uri.encodeComponent(row.sessionId)}',
                            preferences: p,
                            builder: (value, _) => ListView(
                              padding: const EdgeInsets.all(24),
                              children: [
                                ResultPanel(
                                  result: objectOf(value),
                                  preferences: p,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            p.exerciseName(row.exerciseId),
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          Text(
                            '${p.timestampDate(row.createdAt)} · ${p.t(historyStatusKey(row.status))}',
                          ),
                          Text(
                            historyRepetitions(row) == null
                                ? p.t('unavailable')
                                : '${p.number(historyRepetitions(row)!)} ${p.t('reps')}',
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
          ],
          const SizedBox(height: 24),
          PatientReportsPanel(api: widget.api, preferences: p),
        ],
      );
    },
  );
}

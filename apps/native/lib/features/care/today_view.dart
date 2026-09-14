import 'package:flutter/material.dart';

import 'care_repository.dart';
import 'check_in_view_model.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';
import '../analysis/analyze_view.dart';
import '../account/patient_account_view.dart';

const symptomFlags = [
  'pain_increase',
  'dizziness',
  'faintness',
  'unusual_shortness_of_breath',
  'chest_discomfort',
  'new_numbness_or_weakness',
  'instability',
  'other',
];

class TodayView extends StatelessWidget {
  final ApiClient api;
  final Preferences preferences;
  const TodayView({super.key, required this.api, required this.preferences});
  @override
  Widget build(BuildContext context) => ResourceView(
    api: api,
    path: 'patient/today',
    preferences: preferences,
    builder: (data, refresh) {
      final today = objectOf(data), p = preferences;
      final items = rowsOf(today['plan_items']);
      Future<void> open(Map<String, dynamic> item) async {
        await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) =>
                CheckInView(api: api, preferences: p, today: today, item: item),
          ),
        );
        refresh();
      }

      final remaining = items
          .where((v) => v['completion_status'] != 'completed')
          .toList();
      return RefreshIndicator(
        onRefresh: () async => refresh(),
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            Text(
              p.t('welcome'),
              style: Theme.of(context).textTheme.headlineLarge,
            ),
            const SizedBox(height: 12),
            Text(p.t('todayIntro')),
            OutlinedButton(
              onPressed: () async {
                await Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => NotificationsView(api: api, preferences: p),
                  ),
                );
                refresh();
              },
              child: Text(
                '${p.t('notifications')} · ${today['unread_notifications'] ?? 0}',
              ),
            ),
            const SizedBox(height: 28),
            Panel(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(
                    Icons.calendar_month,
                    color: Theme.of(context).colorScheme.primary,
                    size: 32,
                  ),
                  const SizedBox(height: 20),
                  Text(
                    today['plan_title'] ?? p.t('emptyPlan'),
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    items.isEmpty
                        ? p.t('emptyPlanBody')
                        : '${items.length - remaining.length} / ${items.length} ${p.t('complete')}',
                  ),
                  if (remaining.isNotEmpty) ...[
                    const SizedBox(height: 22),
                    FilledButton(
                      onPressed: () => open(remaining.first),
                      child: Text(p.t('start')),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 28),
            Text(
              p.t('assigned'),
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            for (final item in items)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Card(
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16),
                    leading: Icon(
                      item['completion_status'] == 'completed'
                          ? Icons.check_circle
                          : Icons.fitness_center,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    title: Text(
                      p.exerciseName(item['exercise_id']),
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    subtitle: Text(
                      '${item['sets']} ${p.t('sets')} · ${item['reps']} ${p.t('reps')}',
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => open(item),
                  ),
                ),
              ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => AnalyzeView(api: api, preferences: p),
                ),
              ),
              icon: const Icon(Icons.video_camera_back_outlined),
              label: Text(p.t('analyze')),
            ),
            const SizedBox(height: 24),
            Text(
              p.t('analysisDisclaimer'),
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      );
    },
  );
}

class CheckInView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final Map<String, dynamic> today, item;
  const CheckInView({
    super.key,
    required this.api,
    required this.preferences,
    required this.today,
    required this.item,
  });
  @override
  State<CheckInView> createState() => _CheckInViewState();
}

class _CheckInViewState extends State<CheckInView> {
  final form = GlobalKey<FormState>();
  final before = TextEditingController(),
      after = TextEditingController(),
      difficulty = TextEditingController(),
      fatigue = TextEditingController(),
      exertion = TextEditingController(),
      note = TextEditingController();
  String status = 'completed';
  bool symptoms = false, stopped = false, acknowledged = false;
  late final Set<String> flags;
  String? localError, analysisSession;
  late final CheckInViewModel model;
  bool get busy => model.busy;
  bool get saved => model.saved;
  String? get error => localError ?? model.error;
  void modelChanged() {
    if (mounted) setState(() {});
  }

  @override
  void initState() {
    super.initState();
    model = CheckInViewModel(CareRepository(widget.api))
      ..addListener(modelChanged);
    analysisSession = widget.item['analysis_session_id'] as String?;
    status = widget.item['completion_status'] as String? ?? 'completed';
    before.text = widget.item['pain_before']?.toString() ?? '';
    after.text = widget.item['pain_after']?.toString() ?? '';
    difficulty.text = widget.item['difficulty']?.toString() ?? '';
    fatigue.text = widget.item['fatigue']?.toString() ?? '';
    exertion.text = widget.item['perceived_exertion']?.toString() ?? '';
    note.text = widget.item['patient_comment']?.toString() ?? '';
    symptoms = widget.item['symptoms_changed'] == true;
    stopped = widget.item['stopped_due_to_symptoms'] == true;
    flags = Set<String>.from(widget.item['symptom_flags'] as List? ?? []);
  }

  @override
  void dispose() {
    model.removeListener(modelChanged);
    model.dispose();
    before.dispose();
    after.dispose();
    difficulty.dispose();
    fatigue.dispose();
    exertion.dispose();
    note.dispose();
    super.dispose();
  }

  void changed() {
    localError = null;
  }

  Future<void> save() async {
    if (!form.currentState!.validate()) return;
    if ((symptoms || stopped || flags.isNotEmpty) && !acknowledged) {
      setState(() {
        localError = widget.preferences.t('acknowledge');
      });
      return;
    }
    localError = null;
    await model.save({
      'plan_item_id': widget.item['item_id'],
      'scheduled_date': widget.today['date'],
      'completion_status': status,
      'pain_before': int.tryParse(before.text),
      'pain_after': int.tryParse(after.text),
      'difficulty': int.tryParse(difficulty.text),
      'fatigue': int.tryParse(fatigue.text),
      'perceived_exertion': int.tryParse(exertion.text),
      'symptom_flags': flags.toList()..sort(),
      'symptoms_changed': symptoms,
      'stopped_due_to_symptoms': stopped,
      'safety_acknowledged': acknowledged,
      'note': note.text.isEmpty ? null : note.text,
      'analysis_session_id': analysisSession,
    });
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences, item = widget.item;
    Widget pain(
      TextEditingController controller,
      String label, {
      int min = 0,
      int max = 10,
    }) => TextFormField(
      controller: controller,
      enabled: !busy,
      decoration: InputDecoration(labelText: label),
      keyboardType: TextInputType.number,
      onChanged: (_) => changed(),
      validator: (v) =>
          v == null ||
              v.isEmpty ||
              (int.tryParse(v) != null &&
                  int.parse(v) >= min &&
                  int.parse(v) <= max)
          ? null
          : '$min–$max',
    );
    return Scaffold(
      appBar: AppBar(title: Text(p.t('checkIn'))),
      body: SafeArea(
        child: saved
            ? Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.check_circle_outline, size: 56),
                      const SizedBox(height: 20),
                      Text(p.t('saved')),
                      const SizedBox(height: 24),
                      FilledButton(
                        onPressed: () => Navigator.pop(context),
                        child: Text(p.t('done')),
                      ),
                    ],
                  ),
                ),
              )
            : ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  Text(
                    p.exerciseName(item['exercise_id']),
                    style: Theme.of(context).textTheme.headlineLarge,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '${item['sets']} ${p.t('sets')} · ${item['reps']} ${p.t('reps')}',
                  ),
                  if (item['instructions'] != null)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      child: Text(item['instructions']),
                    ),
                  if (item['precautions'] != null) Text(item['precautions']),
                  const SizedBox(height: 20),
                  OutlinedButton(
                    onPressed: () async {
                      final result = await Navigator.push<Map<String, dynamic>>(
                        context,
                        MaterialPageRoute(
                          builder: (_) => AnalyzeView(
                            api: widget.api,
                            preferences: p,
                            exercise: item['exercise_id'],
                            patientId: widget.today['patient_id'],
                            returnResult: true,
                          ),
                        ),
                      );
                      if (mounted && result?['session_id'] is String) {
                        setState(() {
                          analysisSession = result!['session_id'];
                          changed();
                        });
                      }
                    },
                    child: Text(p.t('analyze')),
                  ),
                  if (analysisSession != null) Text(p.t('analysisAttached')),
                  const SizedBox(height: 24),
                  Form(
                    key: form,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        DropdownButtonFormField<String>(
                          initialValue: status,
                          decoration: InputDecoration(labelText: p.t('status')),
                          items:
                              [
                                    ('completed', 'complete'),
                                    ('partial', 'partial'),
                                    ('not_completed', 'missed'),
                                  ]
                                  .map(
                                    (s) => DropdownMenuItem(
                                      value: s.$1,
                                      child: Text(p.t(s.$2)),
                                    ),
                                  )
                                  .toList(),
                          onChanged: busy
                              ? null
                              : (v) => setState(() {
                                  status = v!;
                                  changed();
                                }),
                        ),
                        const SizedBox(height: 20),
                        pain(before, p.t('painBefore')),
                        const SizedBox(height: 20),
                        pain(after, p.t('painAfter')),
                        const SizedBox(height: 20),
                        pain(difficulty, p.t('difficulty'), min: 1, max: 5),
                        const SizedBox(height: 20),
                        pain(fatigue, p.t('fatigue'), min: 1, max: 5),
                        const SizedBox(height: 20),
                        pain(exertion, p.t('exertion')),
                        const SizedBox(height: 16),
                        CheckboxListTile(
                          contentPadding: EdgeInsets.zero,
                          value: symptoms,
                          onChanged: busy
                              ? null
                              : (v) => setState(() {
                                  symptoms = v!;
                                  changed();
                                }),
                          title: Text(p.t('symptoms')),
                        ),
                        CheckboxListTile(
                          contentPadding: EdgeInsets.zero,
                          value: stopped,
                          onChanged: busy
                              ? null
                              : (v) => setState(() {
                                  stopped = v!;
                                  changed();
                                }),
                          title: Text(p.t('stopped')),
                        ),
                        Text(
                          p.t('symptomFlags'),
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        for (final flag in symptomFlags)
                          CheckboxListTile(
                            contentPadding: EdgeInsets.zero,
                            value: flags.contains(flag),
                            onChanged: busy
                                ? null
                                : (value) => setState(() {
                                    if (value == true) {
                                      flags.add(flag);
                                    } else {
                                      flags.remove(flag);
                                    }
                                    changed();
                                  }),
                            title: Text(p.t('flag_$flag')),
                          ),
                        if (symptoms || stopped || flags.isNotEmpty) ...[
                          Text(p.t('safety')),
                          CheckboxListTile(
                            contentPadding: EdgeInsets.zero,
                            value: acknowledged,
                            onChanged: busy
                                ? null
                                : (v) => setState(() {
                                    acknowledged = v!;
                                    changed();
                                  }),
                            title: Text(p.t('acknowledge')),
                          ),
                        ],
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: note,
                          enabled: !busy,
                          maxLines: 3,
                          maxLength: 1000,
                          onChanged: (_) => changed(),
                          decoration: InputDecoration(labelText: p.t('notes')),
                        ),
                        if (error != null)
                          Text(
                            error!,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        const SizedBox(height: 20),
                        FilledButton(
                          onPressed: busy ? null : save,
                          child: Text(p.t(busy ? 'loading' : 'save')),
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

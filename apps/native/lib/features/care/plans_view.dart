import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';
import '../../generated/models.dart';
import 'plans_view_model.dart';

const planNumbers = <(String, String, num, num, bool)>[
  ('sets', 'sets', 1, 20, true),
  ('reps', 'reps', 1, 100, true),
  ('days_per_week', 'daysPerWeek', 1, 7, true),
  ('duration_minutes', 'durationMinutes', 1, 240, false),
  ('rest_interval_seconds', 'restSeconds', 0, 3600, false),
  ('target_rom_degrees', 'targetRom', 0, 360, false),
  ('target_score', 'targetScore', 0, 100, false),
];
const planTexts = [
  ('instructions', 'instructions', 1000),
  ('tempo', 'tempo', 64),
  ('precautions', 'precautions', 1000),
];
const planWeekdays = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
];

class PlansView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final String patientId;
  const PlansView({
    super.key,
    required this.api,
    required this.preferences,
    required this.patientId,
  });
  @override
  State<PlansView> createState() => _PlansViewState();
}

class _PlansViewState extends State<PlansView> {
  late final PlansRepository repository;
  late Future<List<ExercisePlanDetail>> plans;
  bool busy = false;
  String? error;
  @override
  void initState() {
    super.initState();
    repository = PlansRepository(widget.api);
    plans = repository.list(widget.patientId);
  }

  void refresh() => setState(() => plans = repository.list(widget.patientId));
  Future<void> edit([ExercisePlanDetail? seed]) async {
    final changed = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (_) => PlanEditor(
          repository: repository,
          patientId: widget.patientId,
          preferences: widget.preferences,
          seed: seed,
        ),
      ),
    );
    if (changed == true && mounted) refresh();
  }

  Future<void> status(ExercisePlanDetail plan, String value) async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await repository.status(widget.patientId, plan.planId, value);
      if (mounted) refresh();
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return Scaffold(
      appBar: AppBar(title: Text(p.t('carePlans'))),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            FilledButton(
              onPressed: busy ? null : () => edit(),
              child: Text(p.t('newPlan')),
            ),
            if (error != null) Text(error!),
            FutureBuilder<List<ExercisePlanDetail>>(
              future: plans,
              builder: (context, snapshot) {
                if (snapshot.hasError) {
                  return Column(
                    children: [
                      Text(snapshot.error.toString()),
                      OutlinedButton(
                        onPressed: refresh,
                        child: Text(p.t('retry')),
                      ),
                    ],
                  );
                }
                if (!snapshot.hasData) {
                  return const Center(child: CircularProgressIndicator());
                }
                return Column(
                  children: [
                    if (snapshot.data!.isEmpty) Text(p.t('noPlans')),
                    for (final plan in snapshot.data!)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        child: Panel(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Text(
                                plan.title,
                                style: Theme.of(context).textTheme.titleLarge,
                              ),
                              Text(
                                p.t(
                                  plan.status == 'active'
                                      ? 'planActive'
                                      : plan.status == 'paused'
                                      ? 'planPaused'
                                      : 'planCompleted',
                                ),
                              ),
                              Text(plan.createdByName ?? p.t('unavailable')),
                              if (plan.notes != null) Text(plan.notes!),
                              Text(
                                '${plan.startDate == null ? p.t('unavailable') : p.date(plan.startDate!)} – ${plan.endDate == null ? p.t('unavailable') : p.date(plan.endDate!)}',
                              ),
                              for (final item
                                  in plan.items ?? <ExercisePlanItemDetail>[])
                                ExpansionTile(
                                  title: Text(p.exerciseName(item.exerciseId)),
                                  children: [
                                    for (final field in planNumbers)
                                      ListTile(
                                        title: Text(p.t(field.$2)),
                                        subtitle: Text(
                                          item.toJson()[field.$1]?.toString() ??
                                              p.t('unavailable'),
                                        ),
                                      ),
                                    for (final field in planTexts)
                                      if (item.toJson()[field.$1] != null)
                                        ListTile(
                                          title: Text(p.t(field.$2)),
                                          subtitle: Text(
                                            item.toJson()[field.$1],
                                          ),
                                        ),
                                    Text(
                                      (item.scheduleDays ?? [])
                                          .map((day) => p.t(planWeekdays[day]))
                                          .join(' · '),
                                    ),
                                    if (item.requestedMediaUpload == true)
                                      Text(p.t('requestMedia')),
                                    if (item.requiresAiAnalysis == true)
                                      Text(p.t('requireAnalysis')),
                                  ],
                                ),
                              OutlinedButton(
                                onPressed: busy ? null : () => edit(plan),
                                child: Text(p.t('revisePlan')),
                              ),
                              if (plan.status != 'completed') ...[
                                OutlinedButton(
                                  onPressed: busy
                                      ? null
                                      : () => status(
                                          plan,
                                          plan.status == 'active'
                                              ? 'paused'
                                              : 'active',
                                        ),
                                  child: Text(
                                    p.t(
                                      plan.status == 'active'
                                          ? 'pausePlan'
                                          : 'resumePlan',
                                    ),
                                  ),
                                ),
                                OutlinedButton(
                                  onPressed: busy
                                      ? null
                                      : () => status(plan, 'completed'),
                                  child: Text(p.t('completePlan')),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class PlanEditor extends StatefulWidget {
  final PlansRepository repository;
  final String patientId;
  final Preferences preferences;
  final ExercisePlanDetail? seed;
  const PlanEditor({
    super.key,
    required this.repository,
    required this.patientId,
    required this.preferences,
    this.seed,
  });
  @override
  State<PlanEditor> createState() => _PlanEditorState();
}

class _PlanEditorState extends State<PlanEditor> {
  late final PlanEditorModel model;
  late final TextEditingController title, notes, start, end;
  final form = GlobalKey<FormState>();
  late final List<Map<String, dynamic>> items;
  late Future<dynamic> exercises;
  @override
  void initState() {
    super.initState();
    model = PlanEditorModel(widget.repository, widget.patientId);
    title = TextEditingController(text: widget.seed?.title);
    notes = TextEditingController(text: widget.seed?.notes);
    start = TextEditingController(
      text: widget.seed?.startDate?.substring(0, 10),
    );
    end = TextEditingController(text: widget.seed?.endDate?.substring(0, 10));
    items =
        widget.seed?.items
            ?.map(
              (item) => Map<String, dynamic>.from(item.toJson())
                ..['schedule_days'] = List<int>.from(item.scheduleDays ?? []),
            )
            .toList() ??
        [{}];
    exercises = widget.repository.api.request('exercises');
  }

  @override
  void dispose() {
    for (final c in [title, notes, start, end]) {
      c.dispose();
    }
    model.dispose();
    super.dispose();
  }

  Future<void> save() async {
    if (!form.currentState!.validate()) return;
    form.currentState!.save();
    final from = start.text.trim(), to = end.text.trim();
    if (from.isNotEmpty && to.isNotEmpty && to.compareTo(from) < 0) {
      setState(() => model.error = widget.preferences.t('invalidPlanDates'));
      return;
    }
    await model.save({
      'title': title.text.trim(),
      'notes': notes.text.trim().isEmpty ? null : notes.text.trim(),
      'start_date': from.isEmpty ? null : '${from}T00:00:00Z',
      'end_date': to.isEmpty ? null : '${to}T00:00:00Z',
      'items': items
          .map(
            (item) => Map<String, dynamic>.from(item)
              ..remove('item_id')
              ..remove('sort_order')
              ..remove('status'),
          )
          .toList(),
    });
    if (model.done && mounted) Navigator.pop(context, true);
  }

  String? dateValidator(String? value) {
    if (value == null || value.isEmpty) return null;
    final date = DateTime.tryParse(value);
    return RegExp(r'^\d{4}-\d{2}-\d{2}$').hasMatch(value) &&
            date != null &&
            date.toIso8601String().startsWith(value)
        ? null
        : widget.preferences.t('dateFormat');
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return Scaffold(
      appBar: AppBar(
        title: Text(p.t(widget.seed == null ? 'newPlan' : 'revisePlan')),
      ),
      body: SafeArea(
        child: ListenableBuilder(
          listenable: model,
          builder: (context, _) => SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: form,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(p.t('planVersionNotice')),
                  const SizedBox(height: 20),
                  TextFormField(
                    controller: title,
                    enabled: !model.busy,
                    maxLength: 120,
                    decoration: InputDecoration(labelText: p.t('planTitle')),
                    validator: (v) =>
                        (v ?? '').trim().isEmpty ? p.t('planTitle') : null,
                  ),
                  TextFormField(
                    controller: notes,
                    enabled: !model.busy,
                    maxLength: 2000,
                    maxLines: 3,
                    decoration: InputDecoration(labelText: p.t('planNotes')),
                  ),
                  TextFormField(
                    controller: start,
                    enabled: !model.busy,
                    decoration: InputDecoration(
                      labelText: p.t('startDate'),
                      hintText: 'YYYY-MM-DD',
                    ),
                    validator: dateValidator,
                  ),
                  TextFormField(
                    controller: end,
                    enabled: !model.busy,
                    decoration: InputDecoration(
                      labelText: p.t('endDate'),
                      hintText: 'YYYY-MM-DD',
                    ),
                    validator: dateValidator,
                  ),
                  FutureBuilder<dynamic>(
                    future: exercises,
                    builder: (context, snapshot) {
                      if (snapshot.hasError) {
                        return Column(
                          children: [
                            Text(snapshot.error.toString()),
                            OutlinedButton(
                              onPressed: () => setState(
                                () => exercises = widget.repository.api.request(
                                  'exercises',
                                ),
                              ),
                              child: Text(p.t('retry')),
                            ),
                          ],
                        );
                      }
                      if (!snapshot.hasData) {
                        return const Center(child: CircularProgressIndicator());
                      }
                      final choices = rowsOf(snapshot.data);
                      return Column(
                        children: [
                          for (var index = 0; index < items.length; index++)
                            Padding(
                              padding: const EdgeInsets.symmetric(vertical: 20),
                              child: PlanItemForm(
                                key: ObjectKey(items[index]),
                                item: items[index],
                                choices: choices,
                                preferences: p,
                                index: index,
                                enabled: !model.busy,
                                onRemove: items.length == 1
                                    ? null
                                    : () =>
                                          setState(() => items.removeAt(index)),
                              ),
                            ),
                          OutlinedButton(
                            onPressed: model.busy || items.length >= 20
                                ? null
                                : () => setState(() => items.add({})),
                            child: Text(p.t('addExercise')),
                          ),
                          if (model.error != null)
                            Semantics(
                              liveRegion: true,
                              child: Text(
                                model.error!,
                                style: TextStyle(
                                  color: Theme.of(context).colorScheme.error,
                                ),
                              ),
                            ),
                          FilledButton(
                            onPressed: model.busy ? null : save,
                            child: Text(
                              p.t(model.busy ? 'loading' : 'publishPlan'),
                            ),
                          ),
                        ],
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class PlanItemForm extends StatefulWidget {
  final Map<String, dynamic> item;
  final List<Map<String, dynamic>> choices;
  final Preferences preferences;
  final int index;
  final bool enabled;
  final VoidCallback? onRemove;
  const PlanItemForm({
    super.key,
    required this.item,
    required this.choices,
    required this.preferences,
    required this.index,
    required this.enabled,
    this.onRemove,
  });
  @override
  State<PlanItemForm> createState() => _PlanItemFormState();
}

class _PlanItemFormState extends State<PlanItemForm> {
  @override
  Widget build(BuildContext context) {
    final p = widget.preferences, item = widget.item;
    return Panel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            '${p.t('exercise')} ${widget.index + 1}',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          DropdownButtonFormField<String>(
            isExpanded: true,
            initialValue: item['exercise_id'],
            decoration: InputDecoration(labelText: p.t('exercise')),
            items: widget.choices
                .map(
                  (ex) => DropdownMenuItem<String>(
                    value: ex['exercise_id'],
                    child: Text(
                      p.exerciseName(ex['exercise_id']),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                )
                .toList(),
            onChanged: widget.enabled ? (v) => item['exercise_id'] = v : null,
            validator: (v) => v == null ? p.t('chooseExercise') : null,
          ),
          for (final field in planNumbers)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: TextFormField(
                initialValue: item[field.$1]?.toString() ?? '',
                enabled: widget.enabled,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: InputDecoration(labelText: p.t(field.$2)),
                validator: (v) {
                  if ((v ?? '').isEmpty) {
                    return field.$5 ? p.t('requiredDosage') : null;
                  }
                  final n = num.tryParse(v!);
                  return n == null ||
                          !n.isFinite ||
                          n < field.$3 ||
                          n > field.$4 ||
                          (!field.$1.startsWith('target_') &&
                              n != n.roundToDouble())
                      ? p.t('invalidDosage')
                      : null;
                },
                onSaved: (v) =>
                    item[field.$1] = (v ?? '').isEmpty ? null : num.parse(v!),
              ),
            ),
          for (final field in planTexts)
            TextFormField(
              initialValue: item[field.$1],
              enabled: widget.enabled,
              maxLength: field.$3,
              maxLines: field.$1 == 'tempo' ? 1 : 3,
              decoration: InputDecoration(labelText: p.t(field.$2)),
              onSaved: (v) =>
                  item[field.$1] = (v ?? '').trim().isEmpty ? null : v!.trim(),
            ),
          Text(p.t('scheduleDays')),
          for (var day = 0; day < 7; day++)
            CheckboxListTile(
              contentPadding: EdgeInsets.zero,
              value: (item['schedule_days'] as List? ?? []).contains(day),
              title: Text(p.t(planWeekdays[day])),
              onChanged: !widget.enabled
                  ? null
                  : (value) => setState(() {
                      final days = List<int>.from(item['schedule_days'] ?? []);
                      if (value == true) {
                        days.add(day);
                      } else {
                        days.remove(day);
                      }
                      days.sort();
                      item['schedule_days'] = days;
                    }),
            ),
          for (final field in [
            ('requested_media_upload', 'requestMedia'),
            ('requires_ai_analysis', 'requireAnalysis'),
          ])
            CheckboxListTile(
              contentPadding: EdgeInsets.zero,
              value: item[field.$1] == true,
              title: Text(p.t(field.$2)),
              onChanged: !widget.enabled
                  ? null
                  : (v) => setState(() => item[field.$1] = v),
            ),
          OutlinedButton(
            onPressed: widget.enabled ? widget.onRemove : null,
            child: Text(p.t('removeExercise')),
          ),
        ],
      ),
    );
  }
}

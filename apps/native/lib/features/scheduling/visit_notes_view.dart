import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';
import 'visit_notes_model.dart';

class VisitNotesView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final String appointmentId;
  final bool staff;
  final String appointmentTime;
  final String? participant;
  const VisitNotesView({
    super.key,
    required this.api,
    required this.preferences,
    required this.appointmentId,
    required this.staff,
    required this.appointmentTime,
    this.participant,
  });
  @override
  State<VisitNotesView> createState() => _VisitNotesViewState();
}

class _VisitNotesViewState extends State<VisitNotesView> {
  late final VisitNotesModel model;
  final summary = TextEditingController(),
      recommendations = TextEditingController();
  final form = GlobalKey<FormState>();
  bool editing = false, visible = false;
  @override
  void initState() {
    super.initState();
    model = VisitNotesModel(
      VisitNotesRepository(widget.api),
      widget.appointmentId,
      widget.staff,
    )..load();
  }

  @override
  void dispose() {
    model.dispose();
    summary.dispose();
    recommendations.dispose();
    super.dispose();
  }

  Future<void> save() async {
    if (!model.uncertain && !form.currentState!.validate()) return;
    final success = await model.save(
      summary.text,
      recommendations.text,
      visible,
    );
    if (success && mounted) {
      setState(() {
        editing = false;
        summary.clear();
        recommendations.clear();
        visible = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    String? validate(String? value, {bool required = false}) =>
        required && (value ?? '').trim().isEmpty
        ? p.t('requiredField')
        : (value ?? '').runes.length > 10000
        ? p.t('noteTooLong')
        : null;
    return Scaffold(
      appBar: AppBar(title: Text(p.t('visitNotes'))),
      body: AnimatedBuilder(
        animation: model,
        builder: (context, _) => SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                widget.appointmentTime,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              if (widget.participant != null) Text(widget.participant!),
              const SizedBox(height: 16),
              Text(
                p.t(
                  widget.staff
                      ? 'visitNotesStaffHint'
                      : 'visitNotesPatientHint',
                ),
              ),
              if (model.saved)
                Semantics(liveRegion: true, child: Text(p.t('visitNoteSaved'))),
              const SizedBox(height: 16),
              if (model.loading)
                Semantics(
                  label: p.t('loading'),
                  child: const Center(child: CircularProgressIndicator()),
                ),
              if (model.readError != null)
                Semantics(liveRegion: true, child: Text(model.readError!)),
              OutlinedButton(
                onPressed: model.loading ? null : model.load,
                child: Text(p.t('historyRefresh')),
              ),
              if (widget.staff && !editing && model.loaded)
                FilledButton(
                  onPressed: () => setState(() {
                    editing = true;
                    model.saved = false;
                  }),
                  child: Text(p.t('addVisitNote')),
                ),
              if (editing)
                Panel(
                  child: Form(
                    key: form,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          p.t('addVisitNote'),
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: summary,
                          minLines: 4,
                          maxLines: null,
                          enabled: !model.busy && !model.uncertain,
                          decoration: InputDecoration(
                            labelText: p.t('visitSummary'),
                          ),
                          validator: (v) => validate(v, required: true),
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: recommendations,
                          minLines: 3,
                          maxLines: null,
                          enabled: !model.busy && !model.uncertain,
                          decoration: InputDecoration(
                            labelText: p.t('visitRecommendations'),
                          ),
                          validator: validate,
                        ),
                        CheckboxListTile(
                          contentPadding: EdgeInsets.zero,
                          value: visible,
                          onChanged: model.busy || model.uncertain
                              ? null
                              : (value) =>
                                    setState(() => visible = value ?? false),
                          title: Text(p.t('shareVisitNote')),
                        ),
                        Text(p.t('noteVisibilityHint')),
                        if (model.saveError != null)
                          Semantics(
                            liveRegion: true,
                            child: Text(model.saveError!),
                          ),
                        if (model.uncertain) Text(p.t('noteUncertain')),
                        const SizedBox(height: 16),
                        FilledButton(
                          onPressed: model.busy ? null : save,
                          child: Text(
                            p.t(
                              model.busy
                                  ? 'loading'
                                  : model.uncertain
                                  ? 'retrySameNote'
                                  : 'saveVisitNote',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              if (model.loaded && model.notes.isEmpty)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: Text(
                    p.t(widget.staff ? 'noVisitNotes' : 'noSharedVisitNotes'),
                  ),
                ),
              for (final note in model.notes)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Panel(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          '${p.timestampDate(note.createdAt)} · ${p.t(note.patientVisible == true ? 'noteShared' : 'notePrivate')}',
                        ),
                        if (note.authorName != null)
                          Text('${p.t('noteAuthor')}: ${note.authorName}'),
                        const SizedBox(height: 12),
                        Text(
                          p.t('visitSummary'),
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        Text(note.summary),
                        if (note.recommendations?.isNotEmpty == true) ...[
                          const SizedBox(height: 12),
                          Text(
                            p.t('visitRecommendations'),
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          Text(note.recommendations!),
                        ],
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

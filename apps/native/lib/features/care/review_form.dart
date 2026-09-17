import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import 'care_repository.dart';
import '../../core/preferences.dart';

class ReviewForm extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final String patientId, adherenceId;
  final VoidCallback onSaved;
  const ReviewForm({
    super.key,
    required this.api,
    required this.preferences,
    required this.patientId,
    required this.adherenceId,
    required this.onSaved,
  });
  @override
  State<ReviewForm> createState() => _ReviewFormState();
}

class _ReviewFormState extends State<ReviewForm> {
  final form = GlobalKey<FormState>();
  final note = TextEditingController();
  String disposition = 'reviewed_no_change';
  bool attested = false, busy = false;
  String? error;
  @override
  void dispose() {
    note.dispose();
    super.dispose();
  }

  Future<void> save() async {
    if (!form.currentState!.validate()) return;
    if (!attested) {
      setState(() => error = widget.preferences.t('attestation'));
      return;
    }
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await CareRepository(widget.api)
          .review(widget.patientId, widget.adherenceId, {
            'disposition': disposition,
            'note': note.text.trim().isEmpty ? null : note.text.trim(),
            'clinician_attestation': attested,
          });
      widget.onSaved();
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return Form(
      key: form,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: disposition,
            isExpanded: true,
            decoration: InputDecoration(labelText: p.t('disposition')),
            items:
                [
                      'reviewed_no_change',
                      'contacted_patient',
                      'plan_modified',
                      'appointment_scheduled',
                      'referred_for_medical_review',
                    ]
                    .map(
                      (value) => DropdownMenuItem(
                        value: value,
                        child: Text(
                          p.t(value),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    )
                    .toList(),
            onChanged: busy
                ? null
                : (value) => setState(() => disposition = value!),
          ),
          const SizedBox(height: 20),
          TextFormField(
            controller: note,
            enabled: !busy,
            maxLines: 3,
            maxLength: 2000,
            decoration: InputDecoration(labelText: p.t('reviewNote')),
            validator: (value) =>
                disposition == 'reviewed_no_change' &&
                    (value ?? '').trim().isEmpty
                ? p.t('reviewNote')
                : null,
          ),
          CheckboxListTile(
            contentPadding: EdgeInsets.zero,
            value: attested,
            title: Text(p.t('attestation')),
            onChanged: busy
                ? null
                : (value) => setState(() => attested = value!),
          ),
          if (error != null)
            Semantics(
              liveRegion: true,
              child: Text(
                error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: busy ? null : save,
            child: Text(p.t(busy ? 'loading' : 'reviewed')),
          ),
        ],
      ),
    );
  }
}

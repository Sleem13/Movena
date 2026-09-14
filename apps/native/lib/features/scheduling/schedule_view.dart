import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';
import '../../generated/models.dart';
import 'scheduling_repository.dart';
import 'visit_notes_view.dart';
import 'scheduling_view_model.dart';

String appointmentTime(String value, Preferences p) =>
    DateFormat.yMMMd(p.language)
        .add_jm()
        .format(DateTime.parse(value).toLocal());

class ScheduleView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final String role;
  const ScheduleView({
    super.key,
    required this.api,
    required this.preferences,
    required this.role,
  });
  @override
  State<ScheduleView> createState() => _ScheduleViewState();
}

class _ScheduleViewState extends State<ScheduleView>
    with WidgetsBindingObserver {
  late final SchedulingViewModel model;
  @override
  void initState() {
    super.initState();
    model = SchedulingViewModel(SchedulingRepository(widget.api), widget.role)
      ..load();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) model.load();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    model.dispose();
    super.dispose();
  }

  Future<void> book() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (_) => BookingView(
          repository: model.repository,
          preferences: widget.preferences,
          connections: model.connections,
        ),
      ),
    );
    if (result == true) await model.load();
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return ListenableBuilder(
      listenable: model,
      builder: (context, _) {
        final now = DateTime.now();
        final upcoming = model.appointments
            .where(
              (row) =>
                  ['scheduled', 'confirmed'].contains(row.status) &&
                  DateTime.parse(row.endsAt).isAfter(now),
            )
            .toList();
        final history = model.appointments
            .where((row) => !upcoming.contains(row))
            .toList()
            .reversed;
        return RefreshIndicator(
          onRefresh: model.load,
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              Text(
                p.t('appointments'),
                style: Theme.of(context).textTheme.headlineLarge,
              ),
              const SizedBox(height: 12),
              Text(p.t('deviceTimezone')),
              const SizedBox(height: 20),
              FilledButton.icon(
                onPressed: model.loading ? null : book,
                icon: const Icon(Icons.add),
                label: Text(p.t('bookAppointment')),
              ),
              if (widget.role == 'therapist')
                OutlinedButton(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => AvailabilityView(
                        repository: model.repository,
                        preferences: p,
                      ),
                    ),
                  ),
                  child: Text(p.t('availability')),
                ),
              if (model.loading)
                const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                ),
              if (model.error != null)
                Panel(
                  child: Column(
                    children: [
                      Text(model.error!),
                      OutlinedButton(
                        onPressed: model.load,
                        child: Text(p.t('retry')),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 24),
              Text(
                p.t('upcoming'),
                style: Theme.of(context).textTheme.titleLarge,
              ),
              if (!model.loading && upcoming.isEmpty)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24),
                  child: Text(p.t('noAppointments')),
                ),
              for (final row in upcoming) appointment(row),
              if (history.isNotEmpty) ...[
                const SizedBox(height: 24),
                Text(
                  p.t('pastAppointments'),
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                for (final row in history) appointment(row),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget appointment(AppointmentSummary row) {
    final match = model.connections.where(
      (c) =>
          c['patient_id'] == row.patientId &&
          c['therapist_user_id'] == row.therapistUserId,
    );
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: AppointmentTile(
        key: ValueKey('${row.appointmentId}:${row.status}:${row.startsAt}'),
        row: row,
        model: model,
        preferences: widget.preferences,
        participant: match.isEmpty
            ? null
            : match.first[widget.role == 'patient'
                  ? 'therapist_name'
                  : 'patient_name'],
      ),
    );
  }
}

class BookingView extends StatefulWidget {
  final SchedulingRepository repository;
  final Preferences preferences;
  final List<Map<String, dynamic>> connections;
  const BookingView({
    super.key,
    required this.repository,
    required this.preferences,
    required this.connections,
  });
  @override
  State<BookingView> createState() => _BookingViewState();
}

class _BookingViewState extends State<BookingView> {
  late final BookingViewModel model;
  Map<String, dynamic>? connection;
  DateTime day = DateTime.now();
  String mode = 'video';
  @override
  void initState() {
    super.initState();
    model = BookingViewModel(widget.repository);
  }

  @override
  void dispose() {
    model.dispose();
    super.dispose();
  }

  void load() {
    if (connection != null) {
      model.loadSlots(connection!['therapist_user_id'], calendarDay(day));
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return Scaffold(
      appBar: AppBar(title: Text(p.t('bookAppointment'))),
      body: ListenableBuilder(
        listenable: model,
        builder: (context, _) => ListView(
          padding: const EdgeInsets.all(24),
          children: [
            if (model.booked != null) ...[
              const Icon(Icons.check_circle_outline, size: 56),
              Text(p.t('bookingSaved')),
              Text(appointmentTime(model.booked!.startsAt, p)),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: Text(p.t('done')),
              ),
            ] else if (widget.connections.isEmpty)
              Text(p.t('noConnections'))
            else ...[
              DropdownButtonFormField<String>(
                isExpanded: true,
                decoration: InputDecoration(labelText: p.t('careConnection')),
                items: widget.connections
                    .map(
                      (c) => DropdownMenuItem<String>(
                        value: c['assignment_id'],
                        child: Text(
                          '${c['patient_name']} · ${c['therapist_name']}',
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    )
                    .toList(),
                onChanged: model.busy
                    ? null
                    : (value) {
                        setState(
                          () => connection = widget.connections.firstWhere(
                            (c) => c['assignment_id'] == value,
                          ),
                        );
                        load();
                      },
              ),
              const SizedBox(height: 20),
              DateSelector(
                day: day,
                preferences: p,
                enabled: !model.busy,
                onChanged: (value) {
                  setState(() => day = value);
                  load();
                },
              ),
              const SizedBox(height: 20),
              Text(p.t('deviceTimezone')),
              if (model.loadingSlots)
                const Padding(
                  padding: EdgeInsets.all(20),
                  child: Center(child: CircularProgressIndicator()),
                ),
              if (connection != null &&
                  !model.loadingSlots &&
                  model.slots.isEmpty)
                Text(p.t('noSlots')),
              SlotChoices(
                slots: model.slots,
                selected: model.selected,
                preferences: p,
                enabled: !model.busy,
                onSelect: model.choose,
              ),
              const SizedBox(height: 24),
              DropdownButtonFormField<String>(
                initialValue: mode,
                isExpanded: true,
                decoration: InputDecoration(labelText: p.t('deliveryMode')),
                items: [
                  DropdownMenuItem(
                    value: 'video',
                    child: Text(p.t('videoVisit')),
                  ),
                  DropdownMenuItem(
                    value: 'in_person',
                    child: Text(p.t('inPerson')),
                  ),
                ],
                onChanged: model.busy
                    ? null
                    : (value) => setState(() => mode = value!),
              ),
              const SizedBox(height: 20),
              Text(p.t('bookingNoCharge')),
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
              const SizedBox(height: 20),
              FilledButton(
                onPressed:
                    model.busy || connection == null || model.selected == null
                    ? null
                    : () => model.book(connection!, mode),
                child: Text(p.t(model.busy ? 'loading' : 'bookAppointment')),
              ),
              if (connection != null)
                OutlinedButton(
                  onPressed: model.busy ? null : load,
                  child: Text(p.t('refresh')),
                ),
            ],
          ],
        ),
      ),
    );
  }
}

class DateSelector extends StatelessWidget {
  final DateTime day;
  final Preferences preferences;
  final bool enabled;
  final ValueChanged<DateTime> onChanged;
  const DateSelector({
    super.key,
    required this.day,
    required this.preferences,
    required this.enabled,
    required this.onChanged,
  });
  @override
  Widget build(BuildContext context) => OutlinedButton.icon(
    icon: const Icon(Icons.calendar_month),
    label: Text(
      '${preferences.t('calendarDay')}: ${preferences.date(calendarDay(day))}',
    ),
    onPressed: !enabled
        ? null
        : () async {
            final now = DateTime.now();
            final date = await showDatePicker(
              context: context,
              initialDate: day.isBefore(now) ? now : day,
              firstDate: DateTime(now.year, now.month, now.day),
              lastDate: now.add(const Duration(days: 730)),
            );
            if (date != null) onChanged(date);
          },
  );
}

class SlotChoices extends StatelessWidget {
  final List<AppointmentSlot> slots;
  final AppointmentSlot? selected;
  final Preferences preferences;
  final bool enabled;
  final ValueChanged<AppointmentSlot> onSelect;
  const SlotChoices({
    super.key,
    required this.slots,
    required this.selected,
    required this.preferences,
    required this.enabled,
    required this.onSelect,
  });
  @override
  Widget build(BuildContext context) => Wrap(
    spacing: 8,
    runSpacing: 8,
    children: slots
        .map(
          (slot) => Semantics(
            selected: selected?.startsAt == slot.startsAt,
            child: selected?.startsAt == slot.startsAt
                ? FilledButton(
                    onPressed: enabled ? () => onSelect(slot) : null,
                    child: Text(appointmentTime(slot.startsAt, preferences)),
                  )
                : OutlinedButton(
                    onPressed: enabled ? () => onSelect(slot) : null,
                    child: Text(appointmentTime(slot.startsAt, preferences)),
                  ),
          ),
        )
        .toList(),
  );
}

class AppointmentTile extends StatefulWidget {
  final AppointmentSummary row;
  final SchedulingViewModel model;
  final Preferences preferences;
  final String? participant;
  const AppointmentTile({
    super.key,
    required this.row,
    required this.model,
    required this.preferences,
    this.participant,
  });
  @override
  State<AppointmentTile> createState() => _AppointmentTileState();
}

class _AppointmentTileState extends State<AppointmentTile> {
  bool joining = false;
  String? error;
  Future<void> join() async {
    setState(() {
      joining = true;
      error = null;
    });
    try {
      final grant = await widget.model.repository.join(
        widget.row.appointmentId,
      );
      if (!mounted) return;
      final uri = visitUri(grant);
      if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
        throw ApiFailure(widget.preferences.t('joinUnavailable'));
      }
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => joining = false);
    }
  }

  Future<void> cancel() async {
    final changed = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (_) => CancellationView(
          preferences: widget.preferences,
          onSave: (reason) async {
            await widget.model.repository.update(widget.row.appointmentId, {
              'status': 'cancelled',
              'cancellation_reason': reason,
            });
          },
        ),
      ),
    );
    if (changed == true) {
      await widget.model.load();
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences, row = widget.row;
    final active = ['scheduled', 'confirmed'].contains(row.status);
    return Panel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            p.t(
              row.status == 'cancelled' ? 'appointmentCancelled' : row.status,
            ),
            style: TextStyle(color: Theme.of(context).colorScheme.primary),
          ),
          const SizedBox(height: 12),
          Text(
            appointmentTime(row.startsAt, p),
            style: Theme.of(context).textTheme.titleLarge,
          ),
          if (widget.participant != null) Text(widget.participant!),
          const SizedBox(height: 12),
          Text(p.t(row.deliveryMode == 'video' ? 'videoVisit' : 'inPerson')),
          Text('${p.t('paymentStatus')}: ${p.t(row.paymentStatus)}'),
          OutlinedButton(
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => VisitNotesView(
                  api: widget.model.repository.api,
                  preferences: p,
                  appointmentId: row.appointmentId,
                  appointmentTime: appointmentTime(row.startsAt, p),
                  participant: widget.participant,
                  staff: widget.model.role != 'patient',
                ),
              ),
            ),
            child: Text(p.t('visitNotes')),
          ),
          if (active && row.deliveryMode == 'video')
            FilledButton.icon(
              onPressed: joining || widget.model.busy || row.canJoin != true
                  ? null
                  : join,
              icon: const Icon(Icons.videocam_outlined),
              label: Text(
                p.t(row.canJoin == true ? 'joinVisit' : 'joinWindow'),
              ),
            ),
          if (active) ...[
            OutlinedButton(
              onPressed: widget.model.busy
                  ? null
                  : () async {
                      final changed = await Navigator.push<bool>(
                        context,
                        MaterialPageRoute(
                          builder: (_) => RescheduleView(
                            row: row,
                            repository: widget.model.repository,
                            preferences: p,
                          ),
                        ),
                      );
                      if (changed == true) await widget.model.load();
                    },
              child: Text(p.t('reschedule')),
            ),
            OutlinedButton(
              onPressed: widget.model.busy ? null : cancel,
              child: Text(p.t('cancelAppointment')),
            ),
            if (widget.model.role != 'patient') ...[
              if (row.status == 'scheduled')
                OutlinedButton(
                  onPressed: widget.model.busy
                      ? null
                      : () => widget.model.update(row.appointmentId, {
                          'status': 'confirmed',
                        }),
                  child: Text(p.t('confirmAppointment')),
                ),
              OutlinedButton(
                onPressed: widget.model.busy
                    ? null
                    : () => widget.model.update(row.appointmentId, {
                        'status': 'completed',
                      }),
                child: Text(p.t('completeAppointment')),
              ),
              OutlinedButton(
                onPressed: widget.model.busy
                    ? null
                    : () => widget.model.update(row.appointmentId, {
                        'status': 'no_show',
                      }),
                child: Text(p.t('noShowAppointment')),
              ),
            ],
          ],
          if (error != null) Text(error!),
        ],
      ),
    );
  }
}

class CancellationView extends StatefulWidget {
  final Preferences preferences;
  final Future<void> Function(String) onSave;
  const CancellationView({
    super.key,
    required this.preferences,
    required this.onSave,
  });
  @override
  State<CancellationView> createState() => _CancellationViewState();
}

class _CancellationViewState extends State<CancellationView> {
  final form = GlobalKey<FormState>();
  final reason = TextEditingController();
  bool busy = false;
  String? error;
  Future<void> save() async {
    if (busy || !form.currentState!.validate()) return;
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await widget.onSave(reason.text.trim());
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  void dispose() {
    reason.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return Scaffold(
      appBar: AppBar(title: Text(p.t('cancelAppointment'))),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Form(
            key: form,
            child: TextFormField(
              controller: reason,
              enabled: !busy,
              maxLines: 4,
              maxLength: 500,
              decoration: InputDecoration(labelText: p.t('cancellationReason')),
              validator: (value) => (value ?? '').trim().isEmpty
                  ? p.t('cancellationReason')
                  : null,
            ),
          ),
          const SizedBox(height: 20),
          if (error != null) Semantics(liveRegion: true, child: Text(error!)),
          FilledButton(
            onPressed: busy ? null : save,
            child: Text(p.t('cancelAppointment')),
          ),
          OutlinedButton(
            onPressed: busy ? null : () => Navigator.pop(context),
            child: Text(p.t('cancelEdit')),
          ),
        ],
      ),
    );
  }
}

class RescheduleView extends StatefulWidget {
  final AppointmentSummary row;
  final SchedulingRepository repository;
  final Preferences preferences;
  const RescheduleView({
    super.key,
    required this.row,
    required this.repository,
    required this.preferences,
  });
  @override
  State<RescheduleView> createState() => _RescheduleViewState();
}

class _RescheduleViewState extends State<RescheduleView> {
  late final BookingViewModel slots;
  DateTime day = DateTime.now();
  bool busy = false;
  String? error;
  @override
  void initState() {
    super.initState();
    slots = BookingViewModel(widget.repository)
      ..loadSlots(widget.row.therapistUserId, calendarDay(day));
  }

  @override
  void dispose() {
    slots.dispose();
    super.dispose();
  }

  Future<void> save() async {
    if (slots.selected == null) return;
    setState(() => busy = true);
    try {
      await widget.repository.update(
        widget.row.appointmentId,
        slots.selected!.toJson(),
      );
      if (mounted) Navigator.pop(context, true);
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
      appBar: AppBar(title: Text(p.t('reschedule'))),
      body: ListenableBuilder(
        listenable: slots,
        builder: (context, _) => ListView(
          padding: const EdgeInsets.all(24),
          children: [
            DateSelector(
              day: day,
              preferences: p,
              enabled: !busy,
              onChanged: (value) {
                setState(() => day = value);
                slots.loadSlots(widget.row.therapistUserId, calendarDay(day));
              },
            ),
            const SizedBox(height: 20),
            if (slots.loadingSlots)
              const Center(child: CircularProgressIndicator()),
            if (!slots.loadingSlots && slots.slots.isEmpty)
              Text(p.t('noSlots')),
            SlotChoices(
              slots: slots.slots,
              selected: slots.selected,
              preferences: p,
              enabled: !busy,
              onSelect: slots.choose,
            ),
            if (slots.error != null) Text(slots.error!),
            if (error != null) Text(error!),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: busy || slots.selected == null ? null : save,
              child: Text(p.t('saveAppointment')),
            ),
          ],
        ),
      ),
    );
  }
}

class AvailabilityView extends StatefulWidget {
  final SchedulingRepository repository;
  final Preferences preferences;
  const AvailabilityView({
    super.key,
    required this.repository,
    required this.preferences,
  });
  @override
  State<AvailabilityView> createState() => _AvailabilityViewState();
}

class _AvailabilityViewState extends State<AvailabilityView> {
  final zone = TextEditingController(text: 'UTC');
  int weekday = 0;
  TimeOfDay start = const TimeOfDay(hour: 9, minute: 0),
      end = const TimeOfDay(hour: 17, minute: 0);
  bool busy = false, saved = false;
  String? error;
  late Future<List<AvailabilityDetail>> rows;
  static const weekdays = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
  ];
  @override
  void initState() {
    super.initState();
    rows = widget.repository.availability();
  }

  @override
  void dispose() {
    zone.dispose();
    super.dispose();
  }

  Future<void> save() async {
    final from = start.hour * 60 + start.minute,
        to = end.hour * 60 + end.minute;
    if (to <= from) {
      setState(() => error = widget.preferences.t('invalidTimeRange'));
      return;
    }
    setState(() {
      busy = true;
      error = null;
      saved = false;
    });
    try {
      await widget.repository.addAvailability({
        'weekday': weekday,
        'start_minute': from,
        'end_minute': to,
        'timezone_name': zone.text.trim(),
      });
      if (mounted) {
        setState(() {
          rows = widget.repository.availability();
          saved = true;
        });
      }
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
      appBar: AppBar(title: Text(p.t('availability'))),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          FutureBuilder<List<AvailabilityDetail>>(
            future: rows,
            builder: (context, snapshot) {
              if (snapshot.hasError) {
                return Column(
                  children: [
                    Text(snapshot.error.toString()),
                    OutlinedButton(
                      onPressed: () => setState(
                        () => rows = widget.repository.availability(),
                      ),
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
                  if (snapshot.data!.isEmpty) Text(p.t('noAvailability')),
                  for (final row in snapshot.data!)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      child: Text(
                        '${p.t(weekdays[row.weekday])} · ${TimeOfDay(hour: row.startMinute ~/ 60, minute: row.startMinute % 60).format(context)}–${TimeOfDay(hour: (row.endMinute ~/ 60) % 24, minute: row.endMinute % 60).format(context)} · ${row.timezoneName}',
                      ),
                    ),
                ],
              );
            },
          ),
          const SizedBox(height: 24),
          DropdownButtonFormField<int>(
            initialValue: weekday,
            isExpanded: true,
            decoration: InputDecoration(labelText: p.t('weekday')),
            items: List.generate(
              7,
              (i) => DropdownMenuItem(value: i, child: Text(p.t(weekdays[i]))),
            ),
            onChanged: busy
                ? null
                : (value) => setState(() => weekday = value!),
          ),
          const SizedBox(height: 20),
          TextField(
            controller: zone,
            enabled: !busy,
            maxLength: 64,
            decoration: InputDecoration(labelText: p.t('ianaTimezone')),
          ),
          OutlinedButton(
            onPressed: busy
                ? null
                : () async {
                    final value = await showTimePicker(
                      context: context,
                      initialTime: start,
                    );
                    if (value != null) setState(() => start = value);
                  },
            child: Text('${p.t('startTime')}: ${start.format(context)}'),
          ),
          OutlinedButton(
            onPressed: busy
                ? null
                : () async {
                    final value = await showTimePicker(
                      context: context,
                      initialTime: end,
                    );
                    if (value != null) setState(() => end = value);
                  },
            child: Text('${p.t('endTime')}: ${end.format(context)}'),
          ),
          if (error != null) Text(error!),
          if (saved)
            Semantics(liveRegion: true, child: Text(p.t('availabilitySaved'))),
          const SizedBox(height: 20),
          FilledButton(
            onPressed: busy ? null : save,
            child: Text(p.t(busy ? 'loading' : 'addAvailability')),
          ),
        ],
      ),
    );
  }
}

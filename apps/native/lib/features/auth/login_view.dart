import 'package:flutter/material.dart';

import '../../core/preferences.dart';
import '../../core/session.dart';
import 'account_view.dart';

class LoginView extends StatefulWidget {
  final SessionRepository session;
  final Preferences preferences;
  const LoginView({
    super.key,
    required this.session,
    required this.preferences,
  });
  @override
  State<LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  final email = TextEditingController(), password = TextEditingController();
  final form = GlobalKey<FormState>();
  bool busy = false, recovery = false;
  String? error, notice;
  @override
  void dispose() {
    email.dispose();
    password.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    if (!form.currentState!.validate()) return;
    setState(() {
      busy = true;
      error = null;
      notice = null;
    });
    try {
      if (recovery) {
        await widget.session.api.request(
          'auth/forgot-password',
          method: 'POST',
          body: {'email': email.text.trim()},
        );
        if (mounted) {
          setState(() {
            notice = widget.preferences.t('sent');
          });
        }
      } else {
        await widget.session.login(email.text.trim(), password.text);
      }
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
  Widget build(BuildContext context) {
    final t = widget.preferences.t;
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Movena',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        actions: [
          TextButton(
            onPressed: () => widget.preferences.setLanguage(
              widget.preferences.language == 'en' ? 'ar' : 'en',
            ),
            child: Text(
              widget.preferences.language == 'en' ? 'العربية' : 'English',
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 480),
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(28),
              child: Form(
                key: form,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Icon(
                      Icons.waves_rounded,
                      size: 48,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 28),
                    Text(
                      t('welcome'),
                      style: Theme.of(context).textTheme.headlineLarge,
                    ),
                    const SizedBox(height: 16),
                    Text(t('noAccount')),
                    const SizedBox(height: 32),
                    TextFormField(
                      controller: email,
                      decoration: InputDecoration(labelText: t('email')),
                      autofillHints: const [AutofillHints.username],
                      textInputAction: TextInputAction.next,
                      validator: (v) =>
                          v == null || v.trim().isEmpty ? t('email') : null,
                    ),
                    const SizedBox(height: 20),
                    if (!recovery)
                      TextFormField(
                        controller: password,
                        obscureText: true,
                        decoration: InputDecoration(labelText: t('password')),
                        autofillHints: const [AutofillHints.password],
                        onFieldSubmitted: (_) => busy ? null : submit(),
                        validator: (v) =>
                            v == null || v.isEmpty ? t('password') : null,
                      ),
                    if (error != null)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        child: Text(
                          error!,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ),
                    if (notice != null)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        child: Text(notice!),
                      ),
                    const SizedBox(height: 24),
                    FilledButton(
                      onPressed: busy ? null : submit,
                      child: Text(
                        t(
                          busy
                              ? 'loading'
                              : recovery
                              ? 'sendRecovery'
                              : 'login',
                        ),
                      ),
                    ),
                    TextButton(
                      onPressed: busy
                          ? null
                          : () => setState(() {
                              recovery = !recovery;
                              error = null;
                              notice = null;
                            }),
                      child: Text(t(recovery ? 'returnLogin' : 'recover')),
                    ),
                    const SizedBox(height: 32),
                    Text(
                      t('analysisDisclaimer'),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    for (final entry in {
                      'register': 'createAccount',
                      'resend-verification': 'resendVerification',
                    }.entries)
                      TextButton(
                        onPressed: busy
                            ? null
                            : () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => AccountFlowView(
                                    api: widget.session.api,
                                    preferences: widget.preferences,
                                    mode: entry.key,
                                  ),
                                ),
                              ),
                        child: Text(t(entry.value)),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

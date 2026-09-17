import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import 'account_view_model.dart';

class AccountFlowView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final String mode;
  final String? initialToken;
  const AccountFlowView({
    super.key,
    required this.api,
    required this.preferences,
    required this.mode,
    this.initialToken,
  });
  @override
  State<AccountFlowView> createState() => _AccountFlowViewState();
}

class _AccountFlowViewState extends State<AccountFlowView> {
  final form = GlobalKey<FormState>();
  final name = TextEditingController(),
      username = TextEditingController(),
      email = TextEditingController(),
      password = TextEditingController(),
      confirmation = TextEditingController();
  late final AccountViewModel model;
  late String token;
  bool terms = false, privacy = false;
  static const titles = {
    'register': 'createAccount',
    'verify-email': 'verifyEmail',
    'reset-password': 'resetPassword',
    'forgot-password': 'recover',
    'resend-verification': 'resendVerification',
  };
  @override
  void initState() {
    super.initState();
    model = AccountViewModel(widget.api);
    token = widget.initialToken ?? '';
  }

  @override
  void dispose() {
    for (final c in [name, username, email, password, confirmation]) {
      c.dispose();
    }
    token = '';
    model.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    if (!form.currentState!.validate() || model.busy) return;
    final mode = widget.mode;
    if (mode == 'register' && (!terms || !privacy)) return;
    final body = mode == 'register'
        ? {
            'full_name': name.text.trim(),
            'username': username.text.trim(),
            'email': email.text.trim(),
            'password': password.text,
            'role': 'patient',
            'accepted_terms': terms,
            'accepted_privacy': privacy,
          }
        : mode == 'reset-password'
        ? {'token': token, 'new_password': password.text}
        : mode == 'verify-email'
        ? {'token': token}
        : {'email': email.text.trim()};
    await model.submit(mode, body);
    if (mounted && model.done) {
      password.clear();
      confirmation.clear();
      token = '';
    }
  }

  void open(String mode) => Navigator.pushReplacement(
    context,
    MaterialPageRoute(
      builder: (_) => AccountFlowView(
        api: widget.api,
        preferences: widget.preferences,
        mode: mode,
      ),
    ),
  );
  Future<void> returnToLogin() async {
    final api = widget.api;
    try {
      await api.tokens.clear();
      if (!mounted) return;
      Navigator.of(context).popUntil((route) => route.isFirst);
      api.onUnauthorized?.call();
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(widget.preferences.t('accountError'))),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences, mode = widget.mode;
    final secret = mode == 'register' || mode == 'reset-password',
        requiresToken = mode == 'reset-password' || mode == 'verify-email';
    return Scaffold(
      appBar: AppBar(title: Text(p.t(titles[mode]!))),
      body: SafeArea(
        child: ListenableBuilder(
          listenable: model,
          builder: (context, _) => Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520),
              child: ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  if (model.done)
                    Semantics(
                      liveRegion: true,
                      child: Text(p.t(model.successKey!)),
                    )
                  else if (requiresToken && token.isEmpty)
                    Text(p.t('invalidAccountLink'))
                  else
                    Form(
                      key: form,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          if (mode == 'register') ...[
                            field(name, 'fullName', max: 120),
                            field(username, 'username', max: 64, min: 3),
                          ],
                          if (!requiresToken)
                            field(
                              email,
                              'emailAddress',
                              max: 254,
                              emailField: true,
                            ),
                          if (secret) ...[
                            Text(p.t('passwordRules')),
                            field(
                              password,
                              'newPassword',
                              max: 128,
                              secret: true,
                            ),
                            field(
                              confirmation,
                              'confirmPassword',
                              max: 128,
                              secret: true,
                              confirm: true,
                            ),
                          ],
                          if (mode == 'register') ...[
                            CheckboxListTile(
                              contentPadding: EdgeInsets.zero,
                              value: terms,
                              onChanged: model.busy
                                  ? null
                                  : (v) => setState(() => terms = v!),
                              title: Text(p.t('acceptTerms')),
                            ),
                            CheckboxListTile(
                              contentPadding: EdgeInsets.zero,
                              value: privacy,
                              onChanged: model.busy
                                  ? null
                                  : (v) => setState(() => privacy = v!),
                              title: Text(p.t('acceptPrivacy')),
                            ),
                          ],
                          if (model.error != null)
                            Semantics(
                              liveRegion: true,
                              child: Text(
                                p.t(model.errorKey ?? 'accountError'),
                                style: TextStyle(
                                  color: Theme.of(context).colorScheme.error,
                                ),
                              ),
                            ),
                          const SizedBox(height: 20),
                          FilledButton(
                            onPressed:
                                model.busy ||
                                    (mode == 'register' && (!terms || !privacy))
                                ? null
                                : submit,
                            child: Text(
                              p.t(model.busy ? 'loading' : titles[mode]!),
                            ),
                          ),
                        ],
                      ),
                    ),
                  const SizedBox(height: 20),
                  OutlinedButton(
                    onPressed: model.busy ? null : returnToLogin,
                    child: Text(p.t('returnLogin')),
                  ),
                  if (mode != 'resend-verification')
                    TextButton(
                      onPressed: model.busy
                          ? null
                          : () => open('resend-verification'),
                      child: Text(p.t('resendVerification')),
                    ),
                  if (mode == 'reset-password')
                    TextButton(
                      onPressed: model.busy
                          ? null
                          : () => open('forgot-password'),
                      child: Text(p.t('sendRecovery')),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget field(
    TextEditingController controller,
    String label, {
    required int max,
    int min = 1,
    bool secret = false,
    bool confirm = false,
    bool emailField = false,
  }) => Padding(
    padding: const EdgeInsets.only(bottom: 20),
    child: TextFormField(
      controller: controller,
      enabled: !model.busy,
      obscureText: secret,
      maxLength: max,
      autocorrect: !secret,
      enableSuggestions: !secret,
      keyboardType: emailField
          ? TextInputType.emailAddress
          : TextInputType.text,
      autofillHints: secret ? const [AutofillHints.newPassword] : null,
      decoration: InputDecoration(labelText: widget.preferences.t(label)),
      validator: (v) {
        final value = v ?? '';
        if (value.trim().length < min) return widget.preferences.t(label);
        if (secret && !validNewPassword(value)) {
          return widget.preferences.t('passwordRules');
        }
        if (confirm && value != password.text) {
          return widget.preferences.t('passwordMismatch');
        }
        if (emailField && !value.contains('@')) {
          return widget.preferences.t('emailAddress');
        }
        return null;
      },
    ),
  );
}

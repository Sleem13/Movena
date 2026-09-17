import 'dart:io';
import 'dart:async';

import 'package:app_links/app_links.dart';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'core/api_client.dart';
import 'core/session.dart';
import 'core/preferences.dart';
import 'features/auth/login_view.dart';
import 'features/auth/account_view.dart';
import 'features/auth/account_view_model.dart';
import 'features/shell/workspace.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final links = AppLinks();
  const configured = String.fromEnvironment('MOVENA_API_URL');
  if (kReleaseMode && !configured.startsWith('https://')) {
    runApp(
      const MaterialApp(
        home: Scaffold(
          body: Center(
            child: Text('This build needs a configured HTTPS API URL.'),
          ),
        ),
      ),
    );
    return;
  }
  final api = ApiClient(
    configured.isNotEmpty
        ? configured
        : Platform.isAndroid
        ? 'http://10.0.2.2:8020'
        : 'http://127.0.0.1:8020',
    const SecureTokenStore(),
  );
  final session = SessionRepository(api);
  final preferences = Preferences();
  await preferences.restore();
  runApp(
    MovenaApp(
      session: session,
      preferences: preferences,
      accountLinks: links.uriLinkStream,
    ),
  );
  await session.restore();
}

class MovenaApp extends StatefulWidget {
  final SessionRepository session;
  final Preferences preferences;
  final Stream<Uri>? accountLinks;
  const MovenaApp({
    super.key,
    required this.session,
    required this.preferences,
    this.accountLinks,
  });
  @override
  State<MovenaApp> createState() => _MovenaAppState();
}

class _MovenaAppState extends State<MovenaApp> {
  var navigator = GlobalKey<NavigatorState>();
  String? navigatorIdentity;
  StreamSubscription<Uri>? subscription;
  AccountLink? pending;
  SessionRepository get session => widget.session;
  Preferences get preferences => widget.preferences;
  @override
  void initState() {
    super.initState();
    session.addListener(showLink);
    subscription = widget.accountLinks?.listen(
      (uri) {
        final link = AccountLink.parse(uri);
        if (link != null) {
          pending = link;
          showLink();
        }
      },
      onError: (_) {
        /* Never log an incoming credential URL. */
      },
    );
  }

  void showLink() {
    if (session.loading || pending == null) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || pending == null) return;
      final nav = navigator.currentState;
      if (nav == null) return;
      final link = pending!;
      pending = null;
      nav.push(
        MaterialPageRoute(
          builder: (_) => AccountFlowView(
            api: session.api,
            preferences: preferences,
            mode: link.mode,
            initialToken: link.token,
          ),
        ),
      );
    });
    WidgetsBinding.instance.ensureVisualUpdate();
  }

  @override
  void dispose() {
    session.removeListener(showLink);
    subscription?.cancel();
    pending = null;
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: Listenable.merge([session, preferences]),
    builder: (context, _) {
      final identity = session.user?['user_id'] as String?;
      if (identity != navigatorIdentity) {
        navigatorIdentity = identity;
        navigator = GlobalKey<NavigatorState>();
      }
      return MaterialApp(
        key: ValueKey(session.user?['user_id'] ?? 'signed-out'),
        navigatorKey: navigator,
        title: 'Movena',
        debugShowCheckedModeBanner: false,
        theme: movenaTheme(Brightness.light),
        darkTheme: movenaTheme(Brightness.dark),
        themeMode: preferences.themeMode,
        locale: Locale(preferences.language),
        supportedLocales: const [Locale('en'), Locale('ar')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: session.loading
            ? const Scaffold(body: Center(child: CircularProgressIndicator()))
            : session.user == null
            ? LoginView(session: session, preferences: preferences)
            : Workspace(session: session, preferences: preferences),
      );
    },
  );
}

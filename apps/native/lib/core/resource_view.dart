import 'package:flutter/material.dart';

import 'api_client.dart';
import 'preferences.dart';

class ResourceView extends StatefulWidget {
  final ApiClient api;
  final String path;
  final Preferences preferences;
  final Widget Function(dynamic data, VoidCallback refresh) builder;
  const ResourceView({
    super.key,
    required this.api,
    required this.path,
    required this.preferences,
    required this.builder,
  });
  @override
  State<ResourceView> createState() => _ResourceViewState();
}

class _ResourceViewState extends State<ResourceView> {
  late Future<dynamic> result;
  @override
  void initState() {
    super.initState();
    result = widget.api.request(widget.path);
  }

  @override
  void didUpdateWidget(ResourceView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.path != widget.path) result = widget.api.request(widget.path);
  }

  void refresh() => setState(() {
    result = widget.api.request(widget.path);
  });
  @override
  Widget build(BuildContext context) => FutureBuilder<dynamic>(
    future: result,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return Center(
          child: Semantics(
            label: widget.preferences.t('loading'),
            child: const CircularProgressIndicator(),
          ),
        );
      }
      if (snapshot.hasError) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(snapshot.error.toString()),
              const SizedBox(height: 16),
              OutlinedButton(
                onPressed: refresh,
                child: Text(widget.preferences.t('retry')),
              ),
            ],
          ),
        );
      }
      return widget.builder(snapshot.data, refresh);
    },
  );
}

class Panel extends StatelessWidget {
  final Widget child;
  const Panel({super.key, required this.child});
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(padding: const EdgeInsets.all(22), child: child),
  );
}

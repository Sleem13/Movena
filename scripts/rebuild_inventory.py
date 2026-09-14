"""Capture route and data-model baselines without importing the live application."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def dependencies(node):
    return sorted({ast.unparse(call.args[0]) for call in ast.walk(node)
                   if isinstance(call, ast.Call) and getattr(call.func, 'id', '') == 'Depends' and call.args})

def domain(path):
    if any(value in path for value in ('rehab-policy', 'recovery-coach', 'live-coach')): return 'coaching'
    if any(value in path for value in ('catalog', 'checkout', 'payment', 'refund', 'billing', 'package')): return 'commerce'
    if any(value in path for value in ('notification',)): return 'notifications'
    if any(value in path for value in ('appointment', 'availability', 'scheduling')): return 'scheduling'
    if any(value in path for value in ('auth/',)): return 'identity'
    if any(value in path for value in ('admin/', 'dataset', 'training', 'model-registry')): return 'administration'
    if any(value in path for value in ('analysis', 'analyze', 'recognition', 'sessions', 'artifacts', 'exercises')): return 'analysis'
    return 'care'


def inventory() -> dict:
    routes = []
    for path in sorted((ROOT / "backend/app/api").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        prefixes = {}
        router_guards = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if getattr(node.value.func, "id", "") == "APIRouter":
                    prefix = next((k.value.value for k in node.value.keywords if k.arg == "prefix" and isinstance(k.value, ast.Constant)), "")
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            prefixes[target.id] = prefix
                            router_guards[target.id] = dependencies(node.value)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                    continue
                method = decorator.func.attr
                router = getattr(decorator.func.value, "id", "")
                if router not in prefixes or method not in {"get", "post", "put", "patch", "delete", "websocket"}:
                    continue
                if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                    continue
                full_path = prefixes[router] + decorator.args[0].value
                routes.append({"method": method.upper(), "path": full_path,
                               "source": path.relative_to(ROOT).as_posix(), "handler": node.name,
                               "line": node.lineno, 'domain': domain(full_path),
                               'dependency_guards': sorted(set(router_guards[router] + dependencies(node))),
                               'replacement_status': 'legacy_authoritative',
                               'removal_gate': 'Verified domain replacement on native/web, contracts, migration/restore and rollback; see README.md'})
    model_tree = ast.parse((ROOT / "backend/app/db/models.py").read_text(encoding="utf-8"))
    models = [node.name for node in model_tree.body if isinstance(node, ast.ClassDef)]
    relationships = []
    for model in model_tree.body:
        if not isinstance(model, ast.ClassDef): continue
        for field in model.body:
            if not isinstance(field, ast.AnnAssign) or field.value is None: continue
            for call in ast.walk(field.value):
                if isinstance(call, ast.Call) and getattr(call.func, 'id', '') == 'ForeignKey' and call.args:
                    relationships.append({'model': model.name, 'field': ast.unparse(field.target),
                                          'target': ast.literal_eval(call.args[0]),
                                          'on_delete': next((ast.literal_eval(k.value) for k in call.keywords if k.arg == 'ondelete'), None)})
    artifacts = []
    for directory in ['models', 'backend/checkpoints']:
        for path in sorted((ROOT / directory).rglob('*')):
            if not path.is_file() or path.suffix not in {'.pt', '.pkl', '.onnx', '.npy'}: continue
            with path.open('rb') as handle: digest = hashlib.file_digest(handle, 'sha256').hexdigest()
            artifacts.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size,
                              'sha256': digest, 'promotion_status': 'unchanged_existing_artifact'})
    return {"schema_version": 2, "method": "static AST; dependency names do not prove effective object permissions; includes conditional routes, not proof of deployed availability",
            "routes": sorted(routes, key=lambda r: (r["path"], r["method"])), "models": models,
            'foreign_keys': relationships, 'model_artifacts': artifacts,
            'integration_sources': sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'backend/app/services').glob('*.py')
                if any(word in p.name for word in ['payment', 'email', 'artifact', 'telemedicine', 'storage', 'notification'])),
            "native_routes": sorted(p.relative_to(ROOT / "mobile/app").as_posix() for p in (ROOT / "mobile/app").rglob("*.tsx")),
            "web_pages": sorted(p.stem for p in (ROOT / "frontend/src/pages").glob("*.jsx") if ".test" not in p.name)}


if __name__ == "__main__":
    output = ROOT / "docs/rebuild/baseline.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(inventory(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)}")

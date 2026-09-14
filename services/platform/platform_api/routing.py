import json
import re
from functools import lru_cache
from django.conf import settings

PUBLIC = {("POST", f"auth/{name}") for name in ["login", "register", "verify-email", "resend-verification", "forgot-password", "reset-password"]}
PUBLIC |= {("GET", "exercises"), ("GET", "recognition/models"), ("GET", "catalog/services"), ("GET", "catalog/packages")}


@lru_cache
def route_patterns():
    inventory = json.loads((settings.REPO_ROOT / "docs/rebuild/baseline.json").read_text())
    patterns = []
    for row in inventory["routes"]:
        if not row["path"].startswith("/api/v1/") or row["method"] == "WEBSOCKET":
            continue
        path = row["path"][8:]
        # Provider callbacks are not exposed on a second URL during migration.
        if any(word in path for word in ["webhook", "callback"]):
            continue
        expression = re.escape(path)
        expression = re.sub(r"\\\{[^}]+\\\}", r"[^/]+", expression)
        patterns.append((row["method"], re.compile("^" + expression + "$")))
    return patterns


def allowed(method, path):
    if any(part in {".", "..", ""} for part in path.split("/")) or any(c in path for c in "\\%?#\x00"):
        return False
    if method == 'GET' and re.fullmatch(r'(patient|therapist)/appointments/[^/]+/session-notes', path):
        return True  # Additive note readers; the captured v1 baseline stays immutable.
    return any(method == verb and expression.fullmatch(path) for verb, expression in route_patterns())

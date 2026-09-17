"""Replacement service. It never opens the legacy application's database."""
import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
APP_ENV = os.environ.get("MOVENA_ENV", "development")
DEBUG = APP_ENV == "development"
SECRET_KEY = os.environ.get("MOVENA_DJANGO_SECRET", "development-only-not-for-deployment")
if not DEBUG and SECRET_KEY == "development-only-not-for-deployment":
    raise RuntimeError("MOVENA_DJANGO_SECRET must be configured outside development")
ALLOWED_HOSTS = os.environ.get("MOVENA_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
ROOT_URLCONF = "movena.urls"
ASGI_APPLICATION = "movena.asgi.application"
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "rest_framework", "drf_spectacular", "platform_api", "identity"]
MIDDLEWARE = ["platform_api.observability.OutcomeMiddleware", "django.middleware.security.SecurityMiddleware", "django.middleware.common.CommonMiddleware"]
LOGGING = {'version': 1, 'disable_existing_loggers': False,
           'handlers': {'outcomes': {'class': 'logging.StreamHandler'}},
           'loggers': {'movena.outcomes': {'handlers': ['outcomes'], 'level': os.environ.get('MOVENA_OUTCOME_LOG_LEVEL', 'WARNING'), 'propagate': False}}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
APPEND_SLASH = False
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "platform-dev.sqlite3"}}
if os.environ.get("MOVENA_DATABASE_URL"):
    db = urlparse(os.environ["MOVENA_DATABASE_URL"])
    if db.scheme not in {"postgres", "postgresql"}:
        raise RuntimeError("MOVENA_DATABASE_URL must use PostgreSQL")
    from urllib.parse import unquote
    DATABASES["default"] = {"ENGINE": "django.db.backends.postgresql", "NAME": db.path.lstrip("/"),
        "USER": unquote(db.username or ""), "PASSWORD": unquote(db.password or ""),
        "HOST": db.hostname, "PORT": db.port or 5432,
        "OPTIONS": {"sslmode": os.environ.get("MOVENA_DB_SSLMODE", "require")}}
elif not DEBUG:
    raise RuntimeError("MOVENA_DATABASE_URL is required outside development")
LEGACY_API_URL = os.environ.get("MOVENA_LEGACY_API_URL", "http://127.0.0.1:8000").rstrip("/")
IDENTITY_MODE = os.environ.get("MOVENA_IDENTITY_MODE", "legacy").strip().lower()
if IDENTITY_MODE not in {"legacy", "transition"}:
    raise RuntimeError("MOVENA_IDENTITY_MODE must be legacy or transition")
INTERNAL_ASSERTION_SECRET = os.environ.get("MOVENA_INTERNAL_ASSERTION_SECRET", "")
if IDENTITY_MODE == "transition" and len(INTERNAL_ASSERTION_SECRET) < 32:
    raise RuntimeError("Transition identity requires MOVENA_INTERNAL_ASSERTION_SECRET of at least 32 characters")
INTERNAL_ASSERTION_ISSUER = "movena-platform"
INTERNAL_ASSERTION_AUDIENCE = "movena-legacy"
IDENTITY_TRANSFER_CONFIRMATION = os.environ.get('MOVENA_IDENTITY_TRANSFER_CONFIRMATION', '')
if IDENTITY_MODE == 'transition' and IDENTITY_TRANSFER_CONFIRMATION:
    raise RuntimeError('Remove MOVENA_IDENTITY_TRANSFER_CONFIRMATION before enabling transition routing')
FRONTEND_URL = os.environ.get("MOVENA_FRONTEND_URL", "http://localhost:3000").rstrip("/")
front = urlparse(FRONTEND_URL)
if front.scheme not in {"http", "https"} or not front.hostname or front.username or front.password or front.query or front.fragment:
    raise RuntimeError("MOVENA_FRONTEND_URL must be an HTTP(S) origin")
EMAIL_DELIVERY_MODE = os.environ.get("MOVENA_EMAIL_DELIVERY_MODE", "console").strip().lower()
if EMAIL_DELIVERY_MODE not in {"console", "smtp"}:
    raise RuntimeError("MOVENA_EMAIL_DELIVERY_MODE must be console or smtp")
if not DEBUG and IDENTITY_MODE == "transition" and EMAIL_DELIVERY_MODE != "smtp":
    raise RuntimeError("Transition identity requires SMTP email delivery outside development")
EMAIL_BACKEND = ("django.core.mail.backends.smtp.EmailBackend" if EMAIL_DELIVERY_MODE == "smtp"
                 else "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.environ.get("MOVENA_EMAIL_FROM", "no-reply@movena.local")
EMAIL_HOST = os.environ.get("MOVENA_SMTP_HOST", "")
EMAIL_PORT = int(os.environ.get("MOVENA_SMTP_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("MOVENA_SMTP_USERNAME", "")
EMAIL_HOST_PASSWORD = os.environ.get("MOVENA_SMTP_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("MOVENA_SMTP_USE_TLS", "true").strip().lower() in {"1", "true", "yes", "on"}
if EMAIL_DELIVERY_MODE == "smtp" and (not EMAIL_HOST or "@" not in DEFAULT_FROM_EMAIL):
    raise RuntimeError("SMTP delivery requires MOVENA_SMTP_HOST and a valid MOVENA_EMAIL_FROM")
terms_version = os.environ.get("MOVENA_TERMS_VERSION", "").strip()
terms_url = os.environ.get("MOVENA_TERMS_URL", "").strip()
privacy_version = os.environ.get("MOVENA_PRIVACY_VERSION", "").strip()
privacy_url = os.environ.get("MOVENA_PRIVACY_URL", "").strip()
IDENTITY_POLICIES = ({"terms": {"version": terms_version, "url": terms_url},
                      "privacy": {"version": privacy_version, "url": privacy_url}}
                     if all((terms_version, terms_url, privacy_version, privacy_url)) else {})
IDENTITY_CONSENT_VERSIONS = IDENTITY_POLICIES
IDENTITY_REQUIRE_VERIFICATION = True
ACCOUNT_ERASURE_DELAY_DAYS = int(os.environ.get('MOVENA_ACCOUNT_ERASURE_DELAY_DAYS', '30'))
if not 1 <= ACCOUNT_ERASURE_DELAY_DAYS <= 3650:
    raise RuntimeError('MOVENA_ACCOUNT_ERASURE_DELAY_DAYS must be between 1 and 3650')
legacy = urlparse(LEGACY_API_URL)
if legacy.scheme not in {"http", "https"} or not legacy.hostname or legacy.username or legacy.password or legacy.query or legacy.fragment or legacy.path not in {"", "/"}:
    raise RuntimeError("MOVENA_LEGACY_API_URL must be an HTTP(S) origin without credentials")
if not DEBUG and legacy.scheme != "https" and legacy.hostname not in {"localhost", "127.0.0.1", "legacy"}:
    raise RuntimeError("Remote legacy APIs require HTTPS")
if not DEBUG and IDENTITY_MODE == "transition" and front.scheme != "https":
    raise RuntimeError("Transition identity requires an HTTPS MOVENA_FRONTEND_URL outside development")
DATA_UPLOAD_MAX_MEMORY_SIZE = 260 * 1024 * 1024
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (["platform_api.authentication.PlatformSessionAuthentication",
        "platform_api.authentication.LegacyBearerAuthentication"] if IDENTITY_MODE == "transition" else
        ["platform_api.authentication.LegacyBearerAuthentication"]),
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "platform_api.errors.exception_handler",
}
SPECTACULAR_SETTINGS = {"TITLE": "Movena platform API", "VERSION": "2.0.0", "SERVE_INCLUDE_SCHEMA": False}
CELERY_BROKER_URL = os.environ.get("MOVENA_REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
SECURE_CONTENT_TYPE_NOSNIFF = True

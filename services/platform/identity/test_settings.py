import os
import subprocess
import sys
from pathlib import Path
from django.test import SimpleTestCase


class TransitionSettingsTests(SimpleTestCase):
    def environment(self):
        values = os.environ.copy()
        values.update({
            'MOVENA_ENV':'production',
            'MOVENA_DJANGO_SECRET':'production-test-secret-'+'x'*32,
            'MOVENA_DATABASE_URL':'postgresql://user:password@db.example.test:5432/movena',
            'MOVENA_LEGACY_API_URL':'https://legacy.example.test',
            'MOVENA_IDENTITY_MODE':'transition',
            'MOVENA_INTERNAL_ASSERTION_SECRET':'transition-test-secret-'+'x'*32,
            'MOVENA_FRONTEND_URL':'https://app.example.test',
            'MOVENA_EMAIL_DELIVERY_MODE':'console',
        })
        return values

    def import_settings(self, environment):
        root = Path(__file__).resolve().parents[1]
        return subprocess.run([sys.executable, '-c', 'import movena.settings'], cwd=root,
            env=environment, text=True, capture_output=True, timeout=15)

    def test_transition_rejects_console_delivery_outside_development(self):
        result = self.import_settings(self.environment())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires SMTP email delivery', result.stderr)

    def test_transition_accepts_complete_smtp_configuration(self):
        environment = self.environment()
        environment.update({'MOVENA_EMAIL_DELIVERY_MODE':'smtp',
            'MOVENA_EMAIL_FROM':'care@example.test', 'MOVENA_SMTP_HOST':'smtp.example.test'})
        result = self.import_settings(environment)
        self.assertEqual(result.returncode, 0, result.stderr)

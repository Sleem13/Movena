import json
from unittest.mock import Mock, patch
from django.test import TestCase, override_settings
from .models import Account
from .outbox import request_account_projection
from .projection import payload, project, publish_pending
from .tests import account_values


class ProjectionTests(TestCase):
    def setUp(self):
        self.account = Account.objects.create(**account_values(), credential_owner='platform')

    def test_projection_contains_current_authority_but_no_credentials(self):
        value = payload(self.account)
        self.assertEqual(value['user_id'], self.account.pk)
        self.assertEqual(value['token_version'], self.account.token_version)
        self.assertNotIn('password_hash', value)
        self.assertNotIn('credential_owner', value)

    @override_settings(INTERNAL_ASSERTION_SECRET='test-projection-secret-'+'x'*32,
                       INTERNAL_ASSERTION_ISSUER='movena-platform',
                       INTERNAL_ASSERTION_AUDIENCE='movena-legacy',
                       LEGACY_API_URL='http://legacy')
    @patch('identity.projection.httpx.Client')
    def test_projection_signs_exact_method_path_and_body(self, client_class):
        response = Mock(status_code=200)
        response.json.return_value = {'user_id':self.account.pk, 'identity_owner':'platform'}
        client_class.return_value.__enter__.return_value.put.return_value = response
        result = project(self.account)
        self.assertEqual(result['identity_owner'], 'platform')
        _, kwargs = client_class.return_value.__enter__.return_value.put.call_args
        body = kwargs['content']
        import jwt
        token = kwargs['headers']['Authorization'].split(' ', 1)[1]
        claims = jwt.decode(token, 'test-projection-secret-'+'x'*32, algorithms=['HS256'],
            issuer='movena-platform', audience='movena-legacy')
        self.assertEqual(claims['method'], 'PUT')
        self.assertEqual(claims['path'], '/internal/v1/identity/accounts/'+self.account.pk)
        import hashlib
        self.assertEqual(claims['body_sha256'], hashlib.sha256(body).hexdigest())
        self.assertNotIn('password_hash', json.loads(body))

    def test_legacy_owned_account_cannot_be_projected(self):
        self.account.credential_owner = 'legacy'
        with self.assertRaises(ValueError):
            project(self.account)

    @patch('identity.projection.project')
    def test_publisher_marks_exact_intent_and_leaves_concurrent_replacement(self, send):
        first = request_account_projection(self.account)
        result = publish_pending()
        first.refresh_from_db()
        self.assertEqual(result, {'selected':1, 'published':1, 'failed':0})
        self.assertIsNotNone(first.published_at)

        request_account_projection(self.account)
        def replace(_account):
            from django.utils import timezone
            from datetime import timedelta
            request_account_projection(self.account, revision=timezone.now()+timedelta(seconds=1))
        send.side_effect = replace
        result = publish_pending()
        first.refresh_from_db()
        self.assertEqual(result['published'], 0)
        self.assertIsNone(first.published_at)

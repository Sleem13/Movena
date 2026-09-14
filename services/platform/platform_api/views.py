import json
import hashlib
import re
from django.conf import settings
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from . import routing, upstream
from .submissions import reserve, fingerprint_upload
from . import scheduling
from . import accounts
from . import care_notes
from .authentication import PlatformAuth
from . import analysis_jobs


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "api_version": "2", "migration_state": "legacy_authoritative"})


class ActiveAnalysisJobsView(APIView):
    """Return locally known active work so clients can recover after a relaunch."""
    def get(self, request):
        return Response(analysis_jobs.active_for(request.user.user_id))


class BridgeView(APIView):
    """Compatibility is explicit and temporary; authorization remains upstream too."""
    def get_authenticators(self):
        # Public recovery must work even when a client still has an expired
        # session. Never forward that unrelated bearer token to public handlers.
        operation = (self.request.method, self.kwargs.get('path', ''))
        if operation in routing.PUBLIC and operation[0] == 'POST' and operation[1].startswith('auth/'):
            return []
        return super().get_authenticators()

    def get_permissions(self):
        path = self.kwargs.get("path", "")
        if (self.request.method, path) in routing.PUBLIC:
            return [AllowAny()]
        return super().get_permissions()

    def forward(self, request, path):
        if not routing.allowed(request.method, path):
            return Response({"status": "error", "error_code": "NOT_FOUND", "message": "This operation is unavailable."}, status=404)
        platform_auth = request.auth if isinstance(request.auth, PlatformAuth) else None
        legacy_token = None if platform_auth else request.auth
        # Cache the untouched body before parsers inspect upload fingerprints.
        raw_body = request.body
        job_match = re.fullmatch(r'analysis-jobs/([^/]+)(?:/cancel)?', path)
        if job_match and (request.method == 'GET' or (request.method == 'POST' and path.endswith('/cancel'))):
            if not analysis_jobs.owned_or_absent(job_match.group(1), request.user):
                return Response({'status':'error','error_code':'JOB_NOT_FOUND','message':'Analysis job not found.'},status=404)
        scheduling.validate_request(request, path)
        accounts.validate_request(request, path)
        care_notes.validate_request(request, path)
        receipt = None
        if request.method == 'POST' and re.fullmatch(r'therapist/(patients/[^/]+/exercise-plans|appointments/[^/]+/session-notes)', path):
            # Revoked care access must deny even an otherwise replayable receipt.
            access = upstream.request('GET', '/api/v1/' + path, token=legacy_token, principal=platform_auth)
            if access.status_code != 200:
                if access.status_code not in {401, 403, 404}:
                    raise upstream.UpstreamUnavailable()
                return Response({'status':'error','error_code':'PATIENT_ACCESS_DENIED','message':'This care record is not available to you.'}, status=access.status_code)
            canonical = json.dumps(request.data, sort_keys=True, separators=(',', ':')).encode()
            receipt, replay = reserve(request.user.user_id, request.headers.get('Idempotency-Key'), path, hashlib.sha256(canonical).hexdigest())
            if replay:
                result = Response(receipt.response, status=receipt.status_code)
                result['Cache-Control'] = 'no-store'
                result['X-Movena-Idempotency-Replayed'] = 'true'
                return result
        if request.method == 'POST' and path.startswith('analysis-jobs/') and path.count('/') == 1:
            receipt, replay = reserve(request.user.user_id, request.headers.get('Idempotency-Key'), path,
                                      fingerprint_upload(request, request.META.get('QUERY_STRING', '')))
            if replay:
                result = Response(receipt.response, status=receipt.status_code)
                result['Cache-Control'] = 'no-store'
                result['X-Movena-Idempotency-Replayed'] = 'true'
                return result
        # Use the untouched body to preserve multipart boundaries and signed data.
        response = upstream.request(request.method, "/api/v1/" + path, token=legacy_token, principal=platform_auth,
            content=raw_body or None, query=request.META.get("QUERY_STRING", ""),
            content_type=request.content_type and request.META.get("CONTENT_TYPE"),
            idempotency_key=request.headers.get("Idempotency-Key"))
        if 300 <= response.status_code < 400:
            return Response({"status": "error", "error_code": "UPSTREAM_REDIRECT", "message": "This operation is unavailable."}, status=502)
        body = response.content
        content_type = response.headers.get("content-type", "application/json")
        if response.status_code < 300 and scheduling.is_calendar_path(path) and 'application/json' in content_type:
            try:
                body = json.dumps(scheduling.normalize_timestamps(response.json())).encode()
            except ValueError:
                pass
        if path.startswith("analysis-jobs/") and "application/json" in content_type:
            try:
                data = response.json()
                if isinstance(data, dict) and "job_id" in data:
                    data["engine_version"] = "legacy-v1"
                    data["model_version"] = None
                    body = json.dumps(data).encode()
                    if response.status_code < 300:
                        try:
                            analysis_jobs.capture(request.user.user_id, path, data)
                        except (TypeError, ValueError):
                            raise upstream.UpstreamUnavailable() from None
            except ValueError:
                pass
        result = HttpResponse(body, status=response.status_code, content_type=content_type)
        if receipt is not None and response.status_code < 500 and 'application/json' in content_type:
            try:
                receipt.response = json.loads(body)
                receipt.status_code = response.status_code
                receipt.state = 'completed'
                receipt.save(update_fields=['response', 'status_code', 'state'])
            except ValueError:
                pass  # An unreadable response leaves the receipt unresolved, never dispatching twice.
        result["Cache-Control"] = "no-store"
        result["X-Movena-Domain-Owner"] = "legacy-v1"
        # Preserve safe download and retry headers, never upstream cookies.
        for name in ["Content-Disposition", "Retry-After"]:
            if name in response.headers:
                result[name] = response.headers[name]
        return result

    get = post = put = patch = delete = forward


class ContractView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(json.loads((settings.REPO_ROOT / "packages/contracts/openapi.json").read_text()))

"""Request outcomes without identities, URLs, query strings or payloads."""
import json
import logging
from time import perf_counter
from uuid import uuid4

logger = logging.getLogger('movena.outcomes')


class OutcomeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = perf_counter()
        request_id = uuid4().hex
        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        route = getattr(getattr(request, 'resolver_match', None), 'url_name', None) or 'unmatched'
        logger.info(json.dumps({'event': 'http_outcome', 'request_id': request_id,
                               'method': request.method, 'route': route,
                               'status': response.status_code,
                               'duration_ms': round((perf_counter() - started) * 1000, 2)}))
        return response

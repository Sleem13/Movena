from dataclasses import dataclass
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from . import upstream
from identity import sessions


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: str
    profile: dict
    is_authenticated: bool = True


@dataclass(frozen=True)
class PlatformAuth:
    account: object


class PlatformSessionAuthentication(BaseAuthentication):
    """Recognize replacement sessions only when transition mode explicitly enables this class."""
    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header:
            return None
        if len(header) != 2 or header[0].lower() != b'bearer':
            raise AuthenticationFailed('Please log in again.')
        try:
            token = header[1].decode('ascii')
        except UnicodeDecodeError:
            raise AuthenticationFailed('Please log in again.') from None
        if not token.startswith('mv2_'):
            return None
        try:
            account = sessions.authenticate(token)
        except sessions.IdentityDenied:
            raise AuthenticationFailed('Your session is no longer available. Please log in again.') from None
        profile = sessions.profile(account)
        return Principal(account.pk, account.role, profile), PlatformAuth(account)

    def authenticate_header(self, request):
        return 'Bearer'


class LegacyBearerAuthentication(BaseAuthentication):
    """Validate on every request so legacy logout and suspension take effect immediately."""
    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header:
            return None
        if len(header) != 2 or header[0].lower() != b"bearer":
            raise AuthenticationFailed("Please log in again.")
        try:
            token = header[1].decode("ascii")
        except UnicodeDecodeError:
            raise AuthenticationFailed("Please log in again.")
        result = upstream.request("GET", "/api/v1/auth/me", token=token)
        if result.status_code in {401, 403}:
            raise AuthenticationFailed("Your session is no longer available. Please log in again.")
        if result.status_code != 200:
            raise upstream.UpstreamUnavailable()
        try:
            profile = result.json()
            user_id = profile["user_id"]
            role = profile["role"]
            if not isinstance(user_id, str) or not isinstance(role, str):
                raise ValueError("Invalid principal")
        except (ValueError, KeyError, TypeError):
            raise upstream.UpstreamUnavailable()
        return Principal(user_id, role, profile), token

    def authenticate_header(self, request):
        return "Bearer"

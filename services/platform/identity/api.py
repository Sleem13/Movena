"""Identity HTTP contract, live only when explicit transition mode is enabled."""
from dataclasses import dataclass
from django.conf import settings
from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from . import sessions
from .legacy_sessions import authenticate_legacy
from . import admin_service
from .models import Consent
from .models import Account
from . import delivery, provisioning
from . import lifecycle


@dataclass
class Principal:
    account: object
    is_authenticated: bool = True


class SessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header:
            return None
        if len(header) != 2 or header[0].lower() != b'bearer':
            raise AuthenticationFailed('Please log in again.')
        try:
            token = header[1].decode('ascii')
            required = getattr(settings, 'IDENTITY_REQUIRE_VERIFICATION', True)
            if token.startswith('mv2_'):
                account = sessions.authenticate(token, require_verified=required)
            else:
                legacy = getattr(settings, 'IDENTITY_LEGACY_VALIDATION', None)
                if not legacy:
                    raise sessions.IdentityDenied()
                account = authenticate_legacy(token, require_verified=required, **legacy)
        except (UnicodeError, sessions.IdentityDenied):
            raise AuthenticationFailed('Please log in again.') from None
        return Principal(account), token

    def authenticate_header(self, request):
        return 'Bearer'


class IdentityView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        return response


class PublicIdentityView(IdentityView):
    authentication_classes = []
    permission_classes = [AllowAny]


class LoginInput(serializers.Serializer):
    email = serializers.CharField(max_length=320)
    password = serializers.CharField(trim_whitespace=False, max_length=128)


class EmailInput(serializers.Serializer):
    email = serializers.EmailField(max_length=320)


class RegistrationInput(EmailInput):
    username = serializers.CharField(min_length=3, max_length=64)
    full_name = serializers.CharField(min_length=1, max_length=120)
    password = serializers.CharField(min_length=8, max_length=128, trim_whitespace=False)
    role = serializers.ChoiceField(choices=['patient'], default='patient')
    accepted_terms = serializers.BooleanField(default=False)
    accepted_privacy = serializers.BooleanField(default=False)


class TokenInput(serializers.Serializer):
    token = serializers.CharField(min_length=32, max_length=512, trim_whitespace=False)


class ResetInput(TokenInput):
    new_password = serializers.CharField(min_length=8, max_length=128, trim_whitespace=False)


class LoginView(PublicIdentityView):
    def post(self, request):
        values = LoginInput(data=request.data)
        values.is_valid(raise_exception=True)
        try:
            return Response(sessions.login(values.validated_data['email'], values.validated_data['password'],
                require_verified=getattr(settings, 'IDENTITY_REQUIRE_VERIFICATION', True)))
        except sessions.IdentityDenied:
            return Response({'error_code': 'INVALID_CREDENTIALS', 'message': 'Username/email or password is incorrect, or this account is unavailable.'}, status=401)


class RegisterView(PublicIdentityView):
    def post(self, request):
        values = RegistrationInput(data=request.data)
        values.is_valid(raise_exception=True)
        data = values.validated_data
        if not getattr(settings, 'IDENTITY_POLICIES', {}):
            return Response({'error_code':'POLICY_UNAVAILABLE','message':'Account registration is temporarily unavailable.'}, status=503)
        if Account.objects.filter(email__iexact=data['email']).exists():
            return Response({'error_code':'EMAIL_ALREADY_REGISTERED','message':'An account with this email already exists.'}, status=409)
        if Account.objects.filter(username__iexact=data['username']).exists():
            return Response({'error_code':'USERNAME_ALREADY_REGISTERED','message':'An account with this username already exists.'}, status=409)
        try:
            result = provisioning.create(data, role='patient', policies=settings.IDENTITY_POLICIES,
                accepted_terms=data['accepted_terms'], accepted_privacy=data['accepted_privacy'])
        except provisioning.ProvisioningDenied:
            return Response({'error_code':'ACCOUNT_CREATION_DENIED','message':'The account could not be created.'}, status=400)
        try:
            delivery.deliver_recovery(result.verification_delivery)
        except delivery.DeliveryFailed:
            return Response({'error_code':'EMAIL_DELIVERY_FAILED','message':'The account was created, but verification email delivery failed.'}, status=503)
        return Response(sessions.profile(result.account), status=201)


class RecoveryRequestView(PublicIdentityView):
    purpose = None

    def post(self, request):
        values = EmailInput(data=request.data)
        values.is_valid(raise_exception=True)
        secret = sessions.issue_recovery(values.validated_data['email'], self.purpose,
            require_verified=getattr(settings, 'IDENTITY_REQUIRE_VERIFICATION', True))
        try:
            delivery.deliver_recovery(secret)
        except delivery.DeliveryFailed:
            # Preserve the same public result for missing, ineligible, throttled,
            # and temporarily undeliverable accounts.
            pass
        return Response({'status':'success','message':'If the account is eligible, an email has been sent.'})


class ForgotPasswordView(RecoveryRequestView):
    purpose = 'reset'


class ResendVerificationView(RecoveryRequestView):
    purpose = 'verification'


class MeView(IdentityView):
    def get(self, request):
        return Response(sessions.profile(request.user.account))


class LogoutView(IdentityView):
    def post(self, request):
        try:
            sessions.revoke_all(request.user.account)
        except sessions.IdentityDenied:
            raise AuthenticationFailed('Please log in again.') from None
        return Response({'status': 'success', 'message': 'All access tokens for this account were revoked.'})


class VerifyView(PublicIdentityView):
    def post(self, request):
        values = TokenInput(data=request.data)
        values.is_valid(raise_exception=True)
        try:
            sessions.verify_email(values.validated_data['token'])
        except sessions.IdentityDenied:
            return Response({'error_code': 'INVALID_OR_EXPIRED_TOKEN', 'message': 'This verification link is invalid or has expired.'}, status=400)
        return Response({'status': 'success', 'message': 'Email verified. You can now log in.'})


class ResetView(PublicIdentityView):
    def post(self, request):
        values = ResetInput(data=request.data)
        values.is_valid(raise_exception=True)
        try:
            sessions.reset_password(values.validated_data['token'], values.validated_data['new_password'],
                require_verified=getattr(settings, 'IDENTITY_REQUIRE_VERIFICATION', True))
        except sessions.IdentityDenied:
            return Response({'error_code': 'INVALID_OR_EXPIRED_TOKEN', 'message': 'The reset request is invalid or has expired.'}, status=400)
        return Response({'status': 'success', 'message': 'Password updated. You can now log in with the new password.'})


class ReasonInput(serializers.Serializer):
    reason = serializers.CharField(min_length=3, max_length=500)


class StatusInput(ReasonInput):
    status = serializers.ChoiceField(choices=['active', 'paused', 'suspended'])


class RoleInput(ReasonInput):
    role = serializers.ChoiceField(choices=list(admin_service.ROLE_PERMISSIONS))


class AdminPasswordInput(ReasonInput):
    new_password = serializers.CharField(min_length=8, max_length=128, trim_whitespace=False)


class ConsentInput(serializers.Serializer):
    consent_type = serializers.CharField(max_length=64)
    accepted = serializers.BooleanField()
    version = serializers.CharField(max_length=32)


class AdminMutationView(IdentityView):
    serializer_class = None
    operation = None

    def mutate(self, request, user_id):
        values = self.serializer_class(data=request.data)
        values.is_valid(raise_exception=True)
        try:
            target = self.operation(request.user.account, user_id, **values.validated_data)
        except admin_service.MutationDenied:
            return Response({'error_code':'ACCOUNT_MUTATION_DENIED','message':'This account change is unavailable.'}, status=403)
        return Response({'status':'success','user_id':target.pk})


class StatusView(AdminMutationView):
    serializer_class = StatusInput
    operation = staticmethod(admin_service.change_status)
    patch = AdminMutationView.mutate


class RoleView(AdminMutationView):
    serializer_class = RoleInput
    operation = staticmethod(admin_service.change_role)
    patch = AdminMutationView.mutate


class AdminPasswordView(AdminMutationView):
    serializer_class = AdminPasswordInput
    operation = staticmethod(admin_service.admin_reset_password)
    post = AdminMutationView.mutate


class ConsentView(IdentityView):
    def get(self, request):
        if request.user.account.role != 'patient':
            return Response({'error_code':'CONSENT_ACCESS_DENIED','message':'This consent record is unavailable.'}, status=403)
        return Response([{'consent_type':row.consent_type, 'accepted':row.accepted,
            'accepted_at':row.accepted_at, 'version':row.version, 'notes':row.notes}
            for row in Consent.objects.filter(account=request.user.account).order_by('id')])

    def post(self, request):
        values = ConsentInput(data=request.data)
        values.is_valid(raise_exception=True)
        try:
            row = admin_service.set_consent(request.user.account, **values.validated_data,
                allowed_versions=getattr(settings, 'IDENTITY_CONSENT_VERSIONS', {}))
        except admin_service.MutationDenied:
            return Response({'error_code':'CONSENT_UPDATE_DENIED','message':'This consent change is unavailable.'}, status=403)
        return Response({'status':'success','consent_type':row.consent_type,'accepted':row.accepted})


class DataRightsInput(serializers.Serializer):
    request_type = serializers.ChoiceField(choices=sorted(lifecycle.TYPES))
    details = serializers.CharField(max_length=2000, required=False, allow_blank=True, allow_null=True)


class DataRightsView(IdentityView):
    def get(self, request):
        if request.user.account.role != 'patient':
            return Response({'error_code':'DATA_RIGHTS_ACCESS_DENIED','message':'This request history is unavailable.'}, status=403)
        rows = lifecycle.DataRightsRequest.objects.filter(account=request.user.account).order_by('-requested_at')
        return Response([lifecycle.serialize(row) for row in rows])

    def post(self, request):
        values = DataRightsInput(data=request.data)
        values.is_valid(raise_exception=True)
        try:
            row, created = lifecycle.request(request.user.account, **values.validated_data)
        except admin_service.MutationDenied:
            return Response({'error_code':'DATA_RIGHTS_REQUEST_DENIED','message':'This request is unavailable.'}, status=403)
        return Response(lifecycle.serialize(row), status=201 if created else 200)


class DataRightsReviewInput(ReasonInput):
    decision = serializers.ChoiceField(choices=['approve','reject'])


class DataRightsAdminView(IdentityView):
    def get(self, request):
        try:
            admin_service.require_super_admin(request.user.account)
        except admin_service.MutationDenied:
            return Response({'error_code':'DATA_RIGHTS_ACCESS_DENIED','message':'This queue is unavailable.'}, status=403)
        rows = lifecycle.DataRightsRequest.objects.select_related('account').order_by('requested_at')[:500]
        return Response([lifecycle.serialize(row, include_account=True) for row in rows])


class DataRightsReviewView(IdentityView):
    def patch(self, request, request_id):
        values = DataRightsReviewInput(data=request.data)
        values.is_valid(raise_exception=True)
        try:
            row = lifecycle.review(request.user.account, request_id, **values.validated_data,
                erasure_delay_days=getattr(settings, 'ACCOUNT_ERASURE_DELAY_DAYS', 30))
        except admin_service.MutationDenied:
            return Response({'error_code':'DATA_RIGHTS_REVIEW_DENIED','message':'This review is unavailable.'}, status=403)
        return Response(lifecycle.serialize(row))

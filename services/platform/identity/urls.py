"""Replacement identity routes, included only in explicit transition mode."""
from django.urls import path
from .api import (AdminPasswordView, ConsentView, ForgotPasswordView, LoginView, LogoutView,
                  MeView, RegisterView, ResendVerificationView, ResetView, RoleView, StatusView, VerifyView)
from .api import DataRightsAdminView, DataRightsReviewView, DataRightsView

urlpatterns = [path('api/v2/auth/'+name, view.as_view()) for name, view in [
    ('login', LoginView), ('logout', LogoutView), ('me', MeView),
    ('reset-password', ResetView), ('verify-email', VerifyView),
    ('register', RegisterView), ('forgot-password', ForgotPasswordView),
    ('resend-verification', ResendVerificationView),
]]
urlpatterns += [
    path('api/v2/admin/users/<str:user_id>/status', StatusView.as_view()),
    path('api/v2/admin/users/<str:user_id>/role', RoleView.as_view()),
    path('api/v2/admin/users/<str:user_id>/password', AdminPasswordView.as_view()),
    path('api/v2/patient/consents', ConsentView.as_view()),
    path('api/v2/patient/data-rights-requests', DataRightsView.as_view()),
    path('api/v2/admin/platform/data-rights-requests', DataRightsAdminView.as_view()),
    path('api/v2/admin/platform/data-rights-requests/<uuid:request_id>', DataRightsReviewView.as_view()),
]

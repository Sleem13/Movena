from django.conf import settings
from django.urls import include, path
from platform_api.views import ActiveAnalysisJobsView, BridgeView, ContractView, HealthView

urlpatterns = [path("health", HealthView.as_view()), path("api/v2/schema", ContractView.as_view())]
urlpatterns.append(path("api/v2/analysis-jobs", ActiveAnalysisJobsView.as_view()))
if settings.IDENTITY_MODE == 'transition':
    urlpatterns.append(path('', include('identity.urls')))
urlpatterns.append(path("api/v2/<path:path>", BridgeView.as_view()))

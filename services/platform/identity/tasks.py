from celery import shared_task
from .projection import publish_pending


@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=5)
def publish_identity_projections():
    return publish_pending()

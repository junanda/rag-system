from celery import Celery
from app.core.config import settings

celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.tasks.document_task',
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# celery_app.autodiscover_tasks(['app.tasks'])
celery_app.autodiscover_tasks(['app.tasks'])
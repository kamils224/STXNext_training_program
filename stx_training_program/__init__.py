# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from stx_training_program.celery import app as celery_app

__all__ = ('celery_app',)

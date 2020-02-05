from meetenjoy import celery_app
from django.db import transaction

from aggregator.loader.dou import DOUApi, DOULoader


@celery_app.task
def load_dou_meetings():
    dou_api = DOUApi()
    loader = DOULoader(dou_api)
    with transaction.atomic():
        loader.load_meetings()

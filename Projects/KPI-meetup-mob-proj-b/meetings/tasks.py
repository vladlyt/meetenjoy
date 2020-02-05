from datetime import timedelta

import requests
from django.conf import settings
from django.utils.timezone import now

from meetenjoy import celery_app
from meetings.models import Cache


@celery_app.task
def cache_request(url, params):
    response = requests.get(url, params)
    if response.ok:
        print(f"Cached request for url: {url}")
        Cache.objects.get_or_create(
            url=url,
            query_params=params,
            defaults={
                'response_json': response.json(),
                'response_status': response.status_code,
                'expires_after': now() + timedelta(seconds=settings.CACHE_EXPIRES)
            }
        )

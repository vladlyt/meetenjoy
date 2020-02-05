import os

from django.conf import settings

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meetenjoy.settings")

app = Celery("meetenjoy")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "load_dou_meetings": {
        "task": "meetenjoy.aggregator.tasks.load_dou_meetings",
        "schedule": crontab(**settings.DOU_LOAD_CRONTAB),
    },
    "load_meetup_meetings": {
        "task": "meetenjoy.aggregator.tasks.load_meetup_meetings",
        "schedule": crontab(**settings.DOU_MEETUP_CRONTAB),
    },
    "update_meeting_statuses": {
        "task": "meetenjoy.aggregator.tasks.update_meeting_statuses",
        "schedule": crontab(**settings.UPDATE_MEETING_STATUSES_CRONTAB),
    },
}
app.conf.timezone = settings.TIME_ZONE

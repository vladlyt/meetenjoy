from django.utils.timezone import now

from meetenjoy import celery_app
from django.db import transaction

from aggregator.loader.dou import DOUApi, DOULoader
from aggregator.loader.meetup import MeetupApi, MeetupLoader
from meetings.models import Meeting, MeetingStatus


def load(_api, _loader):
    api = _api()
    loader = _loader(api)
    with transaction.atomic():
        return loader.load_meetings()


@celery_app.task
def load_dou_meetings():
    load(DOUApi, DOULoader)


@celery_app.task
def load_meetup_meetings():
    load(MeetupApi, MeetupLoader)


@celery_app.task
def update_meeting_statuses():
    date_now = now()
    for meeting in Meeting.objects.published():
        date = None
        if meeting.start_at is not None:
            date = meeting.start_at
            if meeting.duration:
                date += meeting.duration
        if date is not None and date < date_now:
            meeting.status = MeetingStatus.FINISHED
            meeting.save()




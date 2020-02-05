from django.contrib.auth import get_user_model
from django.db import models
from meetenjoy.enumeration import Enumeration

User = get_user_model()


class MeetingQueryset(models.QuerySet):

    def all(self):
        return self.exclude(status=MeetingStatus.DELETED)

    def published(self):
        return self.filter(status=MeetingStatus.PUBLISHED)

    def full_all(self):
        return super().all()


class MeetingManager(models.Manager):

    def get_queryset(self):
        return MeetingQueryset(self.model, using=self._db)

    def all(self):
        return self.get_queryset().all()

    def full_all(self):
        return self.get_queryset().full_all()

    def published(self) -> models.QuerySet:
        return self.get_queryset().published()


MeetingStatus = Enumeration(
    [
        (0, "DRAFT", 'Draft'),
        (1, "PUBLISHED", 'Published'),
        (2, "CANCELED", 'Canceled'),
        (3, "DELETED", 'Deleted'),
        (4, "FINISHED", 'Finished'),
    ]
)


class Meeting(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    small_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    duration = models.TimeField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=MeetingStatus, default=MeetingStatus.DRAFT)
    location = models.TextField(null=True, blank=True)

    main_photo = models.FileField(upload_to="meetings/", null=True, blank=True)
    photo_url = models.CharField(max_length=400, null=True, blank=True)

    is_main = models.BooleanField(default=True)
    from_site = models.CharField(max_length=128, blank=True, default=True)
    from_url = models.CharField(max_length=256, null=True, blank=True)
    related_id = models.CharField(max_length=64, null=True, blank=True)
    date_string = models.CharField(max_length=128, null=True, blank=True)

    creator = models.ForeignKey(User, related_name="created_meetings", on_delete=models.SET_NULL, null=True, blank=True)
    participants = models.ManyToManyField(User, related_name="following_meetings")
    objects = MeetingManager()


class Tag(models.Model):
    name = models.CharField(max_length=64)
    meetings = models.ManyToManyField("meetings.Meeting", related_name="tags")
    users = models.ManyToManyField(User, related_name="tags")


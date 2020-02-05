from django.db import models


class Notification(models.Model):
    user = models.ForeignKey("accounts.User", related_name="notifications", on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    title = models.CharField(max_length=128)
    body = models.CharField(max_length=128)

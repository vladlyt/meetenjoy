from django.db import models


class Meeting(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

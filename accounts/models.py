from django.db import models
from django.contrib.auth.models import AbstractUser

from django.db.models import Sum

from meetenjoy.enumeration import Enumeration

# TODO decompose

POSSIBLE_RATES = Enumeration([
    (1, "AWFUL"),
    (2, "BAD"),
    (3, "GOOD"),
    (4, "NICE"),
    (5, "AMAZING"),
])


class User(AbstractUser):
    location = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=128, null=True, blank=True)
    photo = models.FileField(upload_to="accounts/", null=True, blank=True)
    is_lector = models.BooleanField(default=False)
    _description = models.TextField(null=True, blank=True)

    @property
    def description(self):
        if self.is_lector:
            return self._description

    @description.setter
    def description(self, description):
        if self.is_lector:
            self._description = description

    def rate(self):
        if self.is_lector:
            return self.rate_summary / self.rate_count

    @property
    def rate_count(self):
        if self.is_lector:
            return self.lector_rates.count()

    @property
    def rate_summary(self):
        if self.is_lector:
            return self.lector_rates.all.aggregate(rate=Sum('rate')).get("rate", 1)

    @property
    def rated_lectors(self):
        return self.visitor_rates.values_list("lector", flat=True)


class Rate(models.Model):
    visitor = models.ForeignKey(User, related_name="visitor_rates", on_delete=models.CASCADE)
    lector = models.ForeignKey(User, related_name="lector_rates", on_delete=models.CASCADE)
    rate = models.SmallIntegerField(choices=POSSIBLE_RATES)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("visitor", "lector")

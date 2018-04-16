from django.db.models import Model, CharField, ForeignKey, BooleanField
from django.contrib.auth.models import User


class UserOptIn(Model):
    class Meta:
        unique_together = [("user", "feature", )]

    user = ForeignKey(to=User)
    feature = CharField(max_length=64, blank=True)
    enabled = BooleanField()
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

class Scrape(models.Model):
    name = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __unicode__(self):
        return self.name
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

class Scrape(models.Model):
    name = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __unicode__(self):
        return self.name

class Journal(models.Model):
    name = models.TextField(unique=True)
    link = models.URLField()

class Author(models.Model):
    name = models.CharField(max_length=300)
    email = models.EmailField(unique=True)

class Article(models.Model):
    title = models.TextField()
    link = models.URLField(unique=True)
    date = models.DateTimeField(null=True, blank=True, default=None)
    author = models.ForeignKey(Author)
    journal = models.ForeignKey(Journal)

class Brick(models.Model):
    url = models.URLField(unique=True)
    site = models.CharField(max_length=140)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True) 

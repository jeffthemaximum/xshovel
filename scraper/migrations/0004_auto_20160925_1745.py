# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-25 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0003_auto_20160925_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
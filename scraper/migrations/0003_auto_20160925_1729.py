# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-25 17:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0002_auto_20160925_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='link',
            field=models.URLField(unique=True),
        ),
    ]

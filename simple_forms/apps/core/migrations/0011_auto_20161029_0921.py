# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-29 09:21
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20161029_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Date'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-21 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20161021_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='martial_status',
            field=models.CharField(choices=[('Single', 'Single'), ('Married', 'Married')], default='Single', max_length=20),
        ),
    ]

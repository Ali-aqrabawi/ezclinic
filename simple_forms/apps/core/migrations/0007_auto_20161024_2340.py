# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-24 23:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20161024_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='martial_status',
            field=models.CharField(choices=[('Unmarried', 'Unmarried'), ('Married', 'Married')], default='Single', max_length=20),
        ),
        migrations.AlterField(
            model_name='person',
            name='sex',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Male', max_length=20),
        ),
    ]

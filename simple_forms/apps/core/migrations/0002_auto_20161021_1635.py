# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-21 16:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='person',
            name='email',
        ),
        migrations.RemoveField(
            model_name='person',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='phone',
        ),
        migrations.AddField(
            model_name='person',
            name='address',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='age',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='person',
            name='files',
            field=models.FileField(null=True, upload_to=b''),
        ),
        migrations.AddField(
            model_name='person',
            name='martial_status',
            field=models.CharField(choices=[('S', 'Single'), ('M', 'Married')], default='Single', max_length=20),
        ),
        migrations.AddField(
            model_name='person',
            name='mobile',
            field=models.IntegerField(default=9),
        ),
        migrations.AddField(
            model_name='person',
            name='name',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='sex',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Femame')], default='Male', max_length=20),
        ),
        migrations.AddField(
            model_name='person',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='person',
            name='last_name',
            field=models.CharField(max_length=500),
        ),
    ]

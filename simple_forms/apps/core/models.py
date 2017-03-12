from __future__ import unicode_literals
import logging
import json
from decimal import Decimal

#from django.contrib.auth.models import Permission, User
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangae import fields, storage
from djangae.db import transaction
from django_countries.fields import CountryField

STATUS_CHOICES = (
    ("Unmarried", ("Unmarried")),
    ("Married", ("Married")),
)

SEX_CHOICES = (
    ("Male", ("Male")),
    ("Female", ("Female")),
)

DENTAL_CHART_CHOICES = (
    ("Deciduous", ("Deciduous")),
    ("Permanent", ("Permanent")),
)


public_storage = storage.CloudStorage(
    bucket='ezclinic16.appspot.com', google_acl='public-read')


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, null=False, blank=False)

    country = CountryField()
    city = models.CharField(max_length=30)
    clinic = models.CharField(max_length=30)


class Person(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=250, null=True)
    last_name = models.CharField(max_length=500)
    age = models.IntegerField(default=100)
    martial_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=("Single"))
    sex = models.CharField( max_length=20, choices=SEX_CHOICES, default=("Male"))
    mobile = models.CharField(max_length=26, default=0011)
    amount_paid = models.DecimalField("money paid", max_digits=10,
                                      decimal_places=2, null=False, default=0)
    amount_left = models.DecimalField("total price", max_digits=10,
                                      decimal_places=2, null=False, default=0)
    note = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    date = models.DateField(("Date"), default=date.today, blank=True)
    time = models.TimeField(("Time"), null=True, blank=True)
    chief_complain = models.CharField(max_length=256, null=True, blank=True)
    treatment_plan = models.CharField(max_length=256, null=True, blank=True)
    treatment_done = models.CharField(max_length=256, null=True, blank=True)

    dental_chart_type = models.CharField(
            max_length=20, choices=DENTAL_CHART_CHOICES, default=("Permanent"))
    dental_chart = models.CharField(max_length=1024, default="{}")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not isinstance(self.amount_paid, Decimal):
            self.amount_paid = Decimal(self.amount_paid or "0")
        if not isinstance(self.amount_left, Decimal):
            self.amount_left = Decimal(self.amount_left or "0")
        with transaction.atomic(xg=True):
            delta = 0
            if self.pk:
                old_state = Person.objects.get(pk=self.pk)
                delta = self.amount_paid - Decimal(old_state.amount_paid or "0")
            else:
                delta = self.amount_paid
            super(Person, self).save(*args, **kwargs)

        if delta > 0:
            Receipt.objects.create(user=self.user, person=self, amount=delta)

        try:
            dc = DentalChart.objects.get(person_id=self.pk)
        except DentalChart.DoesNotExist:
            dc = DentalChart(person_id=self.pk)
        dc.dental_chart_type = self.dental_chart_type
        dc.dental_chart = self.dental_chart
        dc.save()


class Receipt(models.Model):
    user = models.ForeignKey(User)
    person = models.ForeignKey(Person)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class Picture(models.Model):
    picture = models.FileField(
        upload_to='image', storage=public_storage, blank=True)
    person = models.ForeignKey(Person, related_name='pictures')

    def filename(self):

        return self.picture.name.split('/')[-1].split('.')[0]

    def __unicode__(self):
        return self.picture.url


class Diagcode(models.Model):
    diagcode = models.CharField(max_length=256)
    person = models.ForeignKey(Person, related_name='diagcodes')

    class Meta:
        unique_together = ('person', 'diagcode')

    def __unicode__(self):
        return self.diagcode

class DentalChart(models.Model):
    COLORS = {"x": "extraction",
              "red": "missing",
              "yellow": "filling",
              "green": "rct"}


    person = models.ForeignKey(Person, related_name='dental_charts')
    dental_chart_type = models.CharField(
            max_length=20, choices=DENTAL_CHART_CHOICES, default=("Permanent"))
    dental_chart = models.CharField(max_length=1024, default="{}")

    extraction = models.IntegerField(default=0)
    missing = models.IntegerField(default=0)
    filling = models.IntegerField(default=0)
    rct = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        data = json.loads(self.dental_chart)
        self.extraction = 0
        self.missing = 0
        self.filling = 0
        self.rct = 0

        for value in data.values():
            if value in self.COLORS:
                field = self.COLORS[value]
                setattr(self, field, 1 + getattr(self, field))
        super(DentalChart, self).save(*args, **kwargs)


class Event(models.Model):
    user = models.ForeignKey(User)
    text = models.TextField(default='', blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


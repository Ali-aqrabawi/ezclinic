from __future__ import unicode_literals
#from django.contrib.auth.models import Permission, User
from django.contrib.auth.models import Permission
from django.db import models
from django import forms
from datetime import date
from django.contrib.auth.models import AbstractUser
import logging


from djangae import fields, storage
import logging
STATUS_CHOICES = (
    ("Unmarried", ("Unmarried")),
    ("Married", ("Married")),
)

SEX_CHOICES = (
    ("Male", ("Male")),
    ("Female", ("Female")),
)



public_storage = storage.CloudStorage(bucket='ezclinic16.appspot.com',google_acl='public-read')


class User(AbstractUser):
    
    
    country = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    clinic = models.CharField(max_length=30)

class Person(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=250,null=True)
    last_name = models.CharField(max_length=500)
    age= models.IntegerField(default=100)
    martial_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=("Single"))
    sex = models.CharField(max_length=20, choices=SEX_CHOICES, default=("Male"))
    mobile=models.CharField(max_length=26,default=0011)
    amount_paid=models.CharField(max_length=256,null=True)
    amount_left = models.CharField(max_length=256, null=True,blank=True)
    note=models.CharField(max_length=256,null=True,blank=True)
    address=models.CharField(max_length=256,null=True,blank=True)
    date = models.DateField(("Date"), default=date.today,blank=True)
    chief_complain = models.CharField(max_length=256,null=True,blank=True)
    treatment_plan=models.CharField(max_length=256,null=True,blank=True)
    treatment_done=models.CharField(max_length=256,null=True,blank=True)
	
    def __str__(self):
        return self.name

class Picture(models.Model):
    picture = models.FileField(upload_to='image', storage=public_storage,blank=True)
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


class PersonForm(forms.ModelForm):
    pictures = forms.FileField(widget=forms.ClearableFileInput(attrs={'required':False,'multiple': True, 'class': 'form-control'}), required=False)
    class Meta:
        model = Person
        fields = ['name', 'last_name', 'age', 'martial_status', 'mobile', 'sex',
                  'amount_paid','amount_left','note', 'address','date','treatment_done','treatment_plan','chief_complain']
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'class': 'form-control',
                                             'placeholder': 'name'}),
            'last_name': forms.TextInput(attrs={'required': True, 'class': 'form-control',
                                           'placeholder': 'lastname'}),
            'age': forms.TextInput(attrs={'required': True, 'class': 'form-control',
                                           'placeholder': 'age'}),
            'amount_paid': forms.TextInput(attrs={'required': True, 'class': 'form-control',
                                           'placeholder': 'amount paid'}),
            'amount_left': forms.TextInput(attrs={'required': True, 'class': 'form-control',
                                           'placeholder': 'amount left'}),
            'note': forms.TextInput(attrs={'required': False, 'class': 'form-control',
                                           'placeholder': 'Patient History'}),
            'address': forms.TextInput(attrs={'required': False, 'class': 'form-control',
                                           'placeholder': 'Current address'}),
            'chief_complain': forms.TextInput(attrs={'required': False, 'class': 'form-control',
                                           'placeholder': 'chief complain'}),
            'treatment_plan': forms.Textarea(attrs={'required': False, 'class': 'form-control',
                                           'placeholder': 'treatment plan','rows':'3'}),
            'treatment_done': forms.Textarea(attrs={'required': False, 'class': 'form-control',
                                           'placeholder': 'treatment done','rows':'3'}),


        }



    
		

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'country','last_name' , 'first_name','city','clinic']
        	        
		
      





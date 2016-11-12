from __future__ import unicode_literals
from django.contrib.auth.models import Permission, User
from django.db import models
from django import forms
from datetime import date


STATUS_CHOICES = (
    ("Unmarried", ("Unmarried")),
    ("Married", ("Married")),
)

SEX_CHOICES = (
    ("Male", ("Male")),
    ("Female", ("Female")),
)
class Person(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=250,null=True)
    last_name = models.CharField(max_length=500)
    age= models.IntegerField(default=100)
    martial_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=("Single"))
    sex = models.CharField(max_length=20, choices=SEX_CHOICES, default=("Male"))
    mobile=models.CharField(max_length=26,default=0011)
    amount_paid=models.CharField(max_length=256,null=True)
    amount_left = models.CharField(max_length=256, null=True)
    note=models.CharField(max_length=256,null=True)
    address=models.CharField(max_length=256,null=True)
    date = models.DateField(("Date"), default=date.today)
    picture = models.ImageField(null=True,blank=True)

    def __str__(self):
        return self.name

class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ['name', 'last_name', 'age', 'martial_status', 'mobile', 'sex','amount_paid','amount_left','note', 'address','date','picture']
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
            'note': forms.TextInput(attrs={'required': True, 'class': 'form-control',
                                           'placeholder': 'Patient History'}),
            'address': forms.TextInput(attrs={'required': True, 'class': 'form-control',
                                           'placeholder': 'Current address'}),




        }



class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']





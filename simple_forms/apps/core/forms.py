from django import forms

from . import models as m


class PersonForm(forms.ModelForm):
    pictures = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'required': False, 'multiple': True, 'class': 'form-control'}), required=False)
    time = forms.TimeField(input_formats=["%I:%M %p"])

    class Meta:
        model = m.Person
        fields = ['name', 'last_name', 'age', 'martial_status', 'mobile', 'sex',
                  'amount_paid', 'amount_left', 'note', 'address', 'date', 'time',
                  'treatment_done', 'treatment_plan', 'chief_complain',
                   'dental_chart_type', 'dental_chart']
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'class': 'form-control',
                                           'placeholder': 'name'}),
            'last_name': forms.TextInput(attrs={'required': True, 'class': 'form-control',
                                                'placeholder': 'lastname'}),
            'age': forms.TextInput(attrs={'required': False, 'class': 'form-control',
                                          'placeholder': 'age'}),
            'amount_paid': forms.TextInput(attrs={'required': False, 'class': 'form-control',
                                                  'placeholder': 'amount paid'}),
            'amount_left': forms.TextInput(attrs={'required': False, 'class': 'form-control',
                                                  'placeholder': 'amount left'}),
            'note': forms.Textarea(attrs={'required': False, 'class': 'form-control',
                                           'placeholder': 'Patient History',
                                           'rows': '3'}),
            'address': forms.TextInput(attrs={'required': False, 'class': 'form-control',
                                              'placeholder': 'Current address'}),
            'chief_complain': forms.TextInput(attrs={'required': False, 'class': 'form-control',
                                                     'placeholder': 'chief complain'}),
            'treatment_plan': forms.Textarea(attrs={'required': False, 'class': 'form-control',
                                                    'placeholder': 'treatment plan', 'rows': '3'}),
            'treatment_done': forms.Textarea(attrs={'required': False, 'class': 'form-control',
                                                    'placeholder': 'treatment done', 'rows': '3'}),
            'dental_chart_type': forms.RadioSelect(),
            'dental_chart': forms.HiddenInput(),


        }


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = m.User
        fields = ['username', 'email', 'password', 'country',
                  'last_name', 'first_name', 'city', 'clinic']


class EventForm(forms.ModelForm):
    class Meta:
        model = m.Event
        fields = ['text', 'date']


class AppointmentForm(forms.ModelForm):
    time = forms.TimeField(input_formats=["%I:%M %p"], required=False)
    class Meta:
        model = m.Appointment
        fields = ["date", "time"]


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = m.Receipt
        fields = ['amount']


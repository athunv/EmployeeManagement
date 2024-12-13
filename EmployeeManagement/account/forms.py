from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from account.models import *

class EmployerCreationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username', 'email',  'password1', 'password2']

class EmployerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email'] 

class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', [])
        initial_data = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)

        for field in fields:
            field_type = field.field_type
            initial_value = initial_data.get(field.label, None)

            if field_type == 'text':
                self.fields[field.label] = forms.CharField(label=field.label, initial=initial_value)
            elif field_type == 'email':
                self.fields[field.label] = forms.EmailField(label=field.label, initial=initial_value)
            elif field_type == 'number':
                self.fields[field.label] = forms.IntegerField(label=field.label, initial=initial_value)
            elif field_type == 'date':
                self.fields[field.label] = forms.DateField(label=field.label, widget=forms.DateInput(attrs={'type': 'date'}), initial=initial_value)
            elif field_type == 'password':
                self.fields[field.label] = forms.CharField(label=field.label, widget=forms.PasswordInput, initial=initial_value)

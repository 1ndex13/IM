from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')
        widgets = {
            'role': forms.Select(choices=CustomUser.ROLE_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['email'].widget.attrs.update({'placeholder': 'Введите email', 'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Введите имя', 'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Введите фамилию', 'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
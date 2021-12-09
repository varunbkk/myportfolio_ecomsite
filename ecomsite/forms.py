# UserCreationForm comes built-in in Django as part of the auth package
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Customer,Order

class UserCreateform(UserCreationForm):
    # Modifying the widgets of the email, first_name and last_name fields
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, **kwargs):
        user = super().save()
        if Customer.objects.filter(email=self.cleaned_data.get('email')).exists():
            customer = Customer.objects.get(email=self.cleaned_data.get('email'))
            customer.user = user
            customer.save()

        else:

            customer = Customer.objects.create(user=user, first_name=self.cleaned_data.get('first_name'),
                last_name=self.cleaned_data.get('last_name'), email=self.cleaned_data.get('email'))

        return user

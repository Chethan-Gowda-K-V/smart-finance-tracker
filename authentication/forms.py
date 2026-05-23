from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    monthly_income_goal = forms.DecimalField(max_digits=12, decimal_places=2, required=False, initial=0.00)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'monthly_income_goal')

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

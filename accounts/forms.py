from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User, Profile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class ProfileCreationForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    profile_picture = forms.ImageField(required=False)
    role = forms.ChoiceField(choices=[('customer', 'Customer'), ('admin', 'Admin'), ('vendor', 'Vendor')], widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'profile_picture', 'role')
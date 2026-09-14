from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import User, Role, TechnicianProfile
from departments.models import Department

class LoginForm(AuthenticationForm):
    """Clean enterprise styled login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Employee ID or Username',
            'autofocus': True,
            'id': 'login-username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
            'id': 'login-password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Employee self-service profile update form."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'location', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Official Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Extension or Mobile'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plant / Building / Desk'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class UserAdminCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'employee_id', 'role', 'department', 'designation')


class UserAdminChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class UserManagementForm(forms.ModelForm):
    """Admin form for managing enterprise users and roles."""
    class Meta:
        model = User
        fields = [
            'employee_id', 'username', 'first_name', 'last_name',
            'email', 'phone', 'department', 'role', 'designation',
            'location', 'is_active'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ContactVerificationForm(forms.Form):
    """
    Prompted on login to confirm employee Email and Mobile Number
    for real-time Email and SMS ticket updates.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. employee@company.com',
            'id': 'contact-email'
        }),
        help_text="Official email to receive ticket confirmations, replies, and resolution reports."
    )
    phone = forms.CharField(
        required=True,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. +91 98765 43210 or Ext. 3001',
            'id': 'contact-phone'
        }),
        help_text="Mobile number to receive instant SMS alerts when technician responds or resolves issue."
    )
    email_alerts = forms.BooleanField(
        required=False,
        initial=True,
        label="Receive Email Notifications",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'opt-email'})
    )
    sms_alerts = forms.BooleanField(
        required=False,
        initial=True,
        label="Receive Instant SMS Alerts",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'opt-sms'})
    )


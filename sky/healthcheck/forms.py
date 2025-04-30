from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Question, Response, HealthCheckSession

'''
UserRegistrationForm is used to register a new user.
It extends the built-in ModelForm class.
'''
class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email")
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True, initial="Engineer", label="Role")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, help_text="Password must be at least 8 characters long, not common, and not entirely numeric.")
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, help_text="Enter the same password as before, for verification.")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        validate_password(password1)
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

'''
UserSettingsForm is used to update the user's first name, last name and email.
It extends the built-in ModelForm class.
'''
class UserSettingsForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


'''
UserUpdateForm is used to update the user's first name, last name and email, only by the app admin.
It extends the built-in ModelForm class.
'''
class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email")
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True, label="Role")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role']
    
    def __init__(self, *args, **kwargs):
        role_initial = kwargs.pop('role_initial', None)
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        if role_initial:
            self.fields['role'].initial = role_initial


'''
ChangePasswordForm is used to change the user's password.
It extends the built-in Form class.
'''
class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Current Password", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={"class": "form-control"}), help_text="Password must be at least 8 characters long, not common, and not entirely numeric.")
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(attrs={"class": "form-control"}), help_text="Enter the same password as before, for verification.")

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        validate_password(new_password1)
        return new_password1

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Passwords do not match.")
        return new_password2
    


'''
Forms for Responses Questions and Session
'''
class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['answer']
        widgets = {
            'answer': forms.RadioSelect(choices=Response.TRAFFIC_LIGHT_CHOICES)
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class HealthCheckSessionForm(forms.ModelForm):
    class Meta:
        model = HealthCheckSession
        fields = ['name', 'questions']
        widgets = {
            'questions': forms.CheckboxSelectMultiple()
        }
from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
MAX_UPLOAD_SIZE = 2500000
from movie_processor.models import MovieFans

# Used to check username to ensure it only contains letters and numbers
import re

class LoginForm(forms.Form):
    username = forms.CharField(max_length = 20, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    password = forms.CharField(max_length = 200, widget = forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:           
            raise forms.ValidationError("Invalid username/password")
        # We must return the cleaned data we got from our parent.
        return cleaned_data

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    password = forms.CharField(max_length = 200, label='Password', widget = forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    confirm_password = forms.CharField(max_length = 200, label='Confirm password', widget = forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))
    email = forms.CharField(max_length=50, label='E-mail',
                                 widget = forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'}))
    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()
        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm')
        if password and confirm and confirm != password:
            raise forms.ValidationError("Passwords did not match.")
        # We must return the cleaned data we got from our parent.
        return cleaned_data

    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')

        if (re.match('^[a-zA-Z0-9]+$', username) == None):
            raise forms.ValidationError("Username may only contain letters and numbers.")
        
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class profileForm(forms.ModelForm):
    class Meta:
        model = MovieFans
        fields = ('profile_picture',)
    widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'btn'}),
        }

    def clean_picture(self):
        profile_picture = self.cleaned_data['profile_picture']
        if not profile_picture:
            raise forms.ValidationError('You must upload a picture')
        if not profile_picture.content_type or not profile_picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if profile_picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return profile_picture
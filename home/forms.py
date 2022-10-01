from pyexpat import model
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from home.models import UserProfile
from django import forms



class RegistrationForm(UserCreationForm):
	email = forms.EmailField(max_length=255, help_text='Required. Add a valid email address')\

	class Meta:
		model = UserProfile
		fields = ['username', 'email', 'password1', 'password2']
	
	def save(self, commit=True):
		# Save the provided password in hashed format
		# user = super().save(commit=False)
		data = UserProfile.objects.create_user(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username']
        )
		data.set_password(self.cleaned_data["password1"])
		if commit:
			data.save()
		return data

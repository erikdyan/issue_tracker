from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from accounts.models import Account


class AccountForm(forms.ModelForm):
	class Meta:
		model = Account
		fields = ('role',)


class EditUserForm(forms.ModelForm):
	username = forms.CharField(max_length=16)
	first_name = forms.CharField(max_length=16)
	last_name = forms.CharField(max_length=16)
	email = forms.EmailField(max_length=32)

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email')


class LoginForm(forms.Form):
	username = forms.CharField(max_length=16)
	password = forms.CharField(widget=forms.PasswordInput)


class UserForm(UserCreationForm):
	username = forms.CharField(max_length=16)
	first_name = forms.CharField(max_length=16)
	last_name = forms.CharField(max_length=16)
	email = forms.EmailField(max_length=32)

	def clean_email(self):
		data = self.cleaned_data['email']
		if Account.objects.filter(user__email=data):
			raise forms.ValidationError('That email address is already in use.')

		# Always return a value to use as the new cleaned data, even if this method didn't change it.
		return data

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

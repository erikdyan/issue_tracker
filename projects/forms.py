from django import forms

from accounts.models import Account
from projects.models import Project


class AccountModelChoiceField(forms.ModelChoiceField):

	def label_from_instance(self, obj):
		return obj.user.username


class ProjectForm(forms.ModelForm):
	project_manager = AccountModelChoiceField(
		Account.objects.filter(role='admin') |
		Account.objects.filter(role='project_manager')
	)

	def clean_project_manager(self):
		data = self.cleaned_data['project_manager']
		if not (data.role == 'admin' or data.role == 'project_manager'):
			raise forms.ValidationError('Project Manager must have the Admin or Project Manager role.')

		# Always return a value to use as the new cleaned data, even if this method didn't change it.
		return data

	class Meta:
		model = Project
		fields = ('title', 'description', 'project_manager')

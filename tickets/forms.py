from django import forms

from accounts.models import Account
from tickets.models import Ticket


class AccountModelChoiceField(forms.ModelChoiceField):

	def label_from_instance(self, obj):
		return obj.user.username


class EditTicketForm(forms.ModelForm):
	assigned_to = AccountModelChoiceField(
		Account.objects.filter(role='admin') |
		Account.objects.filter(role='project_manager') |
		Account.objects.filter(role='developer')
	)

	def clean_assigned_to(self):
		data = self.cleaned_data['assigned_to']
		if not (data.role == 'admin' or data.role == 'project_manager' or data.role == 'developer'):
			raise forms.ValidationError('Assigned To must have the Admin, Project Manager or Developer role.')

		# Always return a value to use as the new cleaned data, even if this method didn't change it.
		return data

	class Meta:
		model = Ticket
		fields = ('assigned_to', 'priority', 'status', 'type')


class NewTicketForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = ('title', 'description', 'priority', 'type')

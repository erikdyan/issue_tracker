from django.db import models
from django.utils import timezone


class Ticket(models.Model):
	PRIORITY_CHOICES = [
		('low', 'Low'),
		('medium', 'Medium'),
		('high', 'High')
	]

	STATUS_CHOICES = [
		('open', 'Open'),
		('in_progress', 'In Progress'),
		('closed', 'Closed')
	]

	TYPE_CHOICES = [
		('bug', 'Bug'),
		('feature_request', 'Feature Request'),
		('comment', 'Comment')
	]

	title = models.CharField(max_length=32)
	description = models.TextField()
	project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='tickets')
	assigned_to = models.ForeignKey(
		'accounts.Account',
		null=True,
		on_delete=models.SET_NULL,
		related_name='assigned_tickets'
	)
	author = models.ForeignKey('accounts.Account', null=True, on_delete=models.SET_NULL, related_name='created_tickets')
	created_date = models.DateTimeField(default=timezone.now)
	priority = models.TextField(choices=PRIORITY_CHOICES, default='low')
	status = models.TextField(choices=STATUS_CHOICES, default='open')
	type = models.TextField(choices=TYPE_CHOICES)
	updated_date = models.DateTimeField(blank=True, null=True)

	def close(self):
		self.assigned_to = None
		self.status = 'closed'
		self.update()

	def update(self):
		self.updated_date = timezone.now()
		self.save()

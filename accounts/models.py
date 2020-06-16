from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
	ROLE_CHOICES = [
		('user', 'User'),
		('developer', 'Developer'),
		('project_manager', 'Project Manager'),
		('admin', 'Admin')
	]

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	role = models.TextField(choices=ROLE_CHOICES, default='user')

	def new_notifications(self):
		return self.notifications.filter(read=False)

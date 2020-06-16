from django.db import models
from django.utils import timezone


class Notification(models.Model):
	title = models.TextField()
	text = models.TextField()
	created_date = models.DateTimeField(default=timezone.now)
	read = models.BooleanField(default=False)
	recipient = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='notifications')

	def mark_read(self):
		self.read = True
		self.save()

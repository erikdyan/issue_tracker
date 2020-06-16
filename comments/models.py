from django.db import models
from django.utils import timezone


class Comment(models.Model):
	text = models.TextField()
	author = models.ForeignKey('accounts.Account', null=True, on_delete=models.SET_NULL, related_name='comments')
	created_date = models.DateTimeField(default=timezone.now)
	ticket = models.ForeignKey('tickets.Ticket', on_delete=models.CASCADE, related_name='comments')

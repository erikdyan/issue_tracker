from django.db import models
from django.utils import timezone


class Project(models.Model):
	title = models.CharField(max_length=32)
	description = models.TextField()
	created_date = models.DateTimeField(default=timezone.now)
	project_manager = models.ForeignKey(
		'accounts.Account',
		null=True,
		on_delete=models.SET_NULL,
		related_name='projects'
	)
	archived = models.BooleanField(default=False)
	archived_date = models.DateTimeField(blank=True, null=True)

	def archive(self):
		self.archived = True
		self.archived_date = timezone.now()
		self.project_manager = None
		self.save()

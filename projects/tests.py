from django.test import TestCase
from django.utils import timezone

from accounts.models import Account
from notifications.models import Notification
from projects.models import Project


class ProjectsTests(TestCase):

	def setUp(self):
		# Create admin account.
		self.client.post('/accounts/signup/', data={
			'username': 'MaryMagdalene',
			'first_name': 'Mary',
			'last_name': 'Magdalene',
			'email': 'Mary@magdalene.co.uk',
			'password1': 'TestPassword',
			'password2': 'TestPassword',
			'role': 'admin'
		})

		# Create project manager account.
		self.client.post('/accounts/signup/', data={
			'username': 'LadyMargaret',
			'first_name': 'Margaret',
			'last_name': 'Beaufort',
			'email': 'Margaret@beaufort.co.uk',
			'password1': 'TestPassword',
			'password2': 'TestPassword',
			'role': 'project_manager'
		})

		# Create developer account.
		self.client.post('/accounts/signup/', data={
			'username': 'PhillipPullman',
			'first_name': 'Phillip',
			'last_name': 'Pullman',
			'email': 'Phillip@pullman.co.uk',
			'password1': 'TestPassword',
			'password2': 'TestPassword',
			'role': 'developer'
		})

		# Create user account.
		self.client.post('/accounts/signup/', data={
			'username': 'J.R.R.Tolkien',
			'first_name': 'John',
			'last_name': 'Tolkien',
			'email': 'John@tolkien.co.uk',
			'password1': 'TestPassword',
			'password2': 'TestPassword',
			'role': 'user'
		})

		# Create demo account.
		self.client.post('/accounts/signup/', data={
			'username': 'WilliamMorris',
			'first_name': 'William',
			'last_name': 'Morris',
			'email': 'William@morris.co.uk',
			'password1': 'TestPassword',
			'password2': 'TestPassword',
			'role': 'admin',
			'demo': True
		})

		# Create a project.
		self.login_as_admin()
		self.client.post('/projects/new/', data={
			'title': 'Oxford University',
			'description': 'University in England',
			'project_manager': Account.objects.get(pk=1).id
		})
		self.client.get('/accounts/logout/')

	def login_as_admin(self):
		self.client.post('/accounts/login/', data={'username': 'MaryMagdalene', 'password': 'TestPassword'})

	def login_as_project_manager(self):
		self.client.post('/accounts/login/', data={'username': 'LadyMargaret', 'password': 'TestPassword'})

	def login_as_developer(self):
		self.client.post('/accounts/login/', data={'username': 'PhillipPullman', 'password': 'TestPassword'})

	def login_as_user(self):
		self.client.post('/accounts/login/', data={'username': 'J.R.R.Tolkien', 'password': 'TestPassword'})

	def login_as_demo(self):
		self.client.post('/accounts/login/', data={'username': 'WilliamMorris', 'password': 'TestPassword'})

	#########################
	# Project archive tests #
	#########################

	def test_admins_can_archive_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertEqual(True, Project.objects.get(pk=1).archived)

	def test_project_managers_can_archive_their_projects(self):
		self.login_as_project_manager()
		self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=2).id
		})

		self.client.get('/projects/2/archive/')

		self.assertEqual(True, Project.objects.get(pk=2).archived)

	def test_project_managers_cannot_archive_other_projects(self):
		self.login_as_project_manager()
		self.assertEqual(404, self.client.get('/projects/1/archive/').status_code)

	def test_developers_cannot_archive_project(self):
		self.login_as_developer()
		self.assertEqual(404, self.client.get('/projects/1/archive/').status_code)

	def test_users_cannot_archive_project(self):
		self.login_as_user()
		self.assertEqual(404, self.client.get('/projects/1/archive/').status_code)

	def test_demo_accounts_cannot_archive_project(self):
		self.login_as_demo()
		self.assertEqual(404, self.client.get('/projects/1/archive/').status_code)

	def test_project_archive_sends_notification_to_project_project_manager(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=2).recipient.user.username)

	def test_project_archive_redirects_after_archiving_projects(self):
		self.login_as_admin()

		response = self.client.get('/projects/1/archive/')

		self.assertEqual(302, response.status_code)
		self.assertEqual('/projects/1/', response['location'])

	##############################
	# Project archive list tests #
	##############################

	def test_admins_can_view_project_archive_list(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/projects/archive/'), 'projects/project_archive_list.html')

	def test_project_managers_can_view_project_archive_list(self):
		self.login_as_project_manager()
		self.assertTemplateUsed(self.client.get('/projects/archive/'), 'projects/project_archive_list.html')

	def test_developers_can_view_project_archive_list(self):
		self.login_as_developer()
		self.assertTemplateUsed(self.client.get('/projects/archive/'), 'projects/project_archive_list.html')

	def test_users_can_view_project_archive_list(self):
		self.login_as_user()
		self.assertTemplateUsed(self.client.get('/projects/archive/'), 'projects/project_archive_list.html')

	def test_project_archive_list_lists_all_archived_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertIn('Oxford University', self.client.get('/projects/archive/').content.decode())

	def test_project_archive_list_does_not_list_active_projects(self):
		self.login_as_admin()
		self.assertNotIn('Oxford University', self.client.get('/projects/archive/').content.decode())

	######################################
	# Project detail ticket closed tests #
	######################################

	def test_admins_can_view_project_detail_ticket_closed(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/projects/1/closed/'), 'projects/project_detail_ticket_closed.html')

	def test_project_managers_can_view_project_detail_ticket_closed(self):
		self.login_as_project_manager()
		self.assertTemplateUsed(self.client.get('/projects/1/closed/'), 'projects/project_detail_ticket_closed.html')

	def test_developers_can_view_project_detail_ticket_closed(self):
		self.login_as_developer()
		self.assertTemplateUsed(self.client.get('/projects/1/closed/'), 'projects/project_detail_ticket_closed.html')

	def test_users_can_view_project_detail_ticket_closed(self):
		self.login_as_user()
		self.assertTemplateUsed(self.client.get('/projects/1/closed/'), 'projects/project_detail_ticket_closed.html')

	def test_project_detail_ticket_closed_renders_correct_project_information(self):
		self.login_as_admin()

		response = self.client.get('/projects/1/').content.decode()

		self.assertIn('Oxford University', response)
		self.assertIn('University in England', response)
		self.assertIn('MaryMagdalene', response)

	def test_project_detail_ticket_closed_lists_closed_tickets(self):
		self.login_as_admin()

		self.client.post('/tickets/1/new/', data={
			'title': 'Computer Science',
			'description': 'A department',
			'created_date': timezone.now(),
			'priority': 'low',
			'type': 'comment'
		})
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'low',
			'status': 'closed',
			'type': 'comment'
		})

		self.assertIn('Computer Science', self.client.get('/projects/1/closed/').content.decode())

	def test_project_detail_ticket_closed_does_not_list_open_tickets(self):
		self.login_as_admin()
		self.client.post('/tickets/1/new/', data={
			'title': 'Computer Science',
			'description': 'A department',
			'created_date': timezone.now(),
			'priority': 'low',
			'type': 'comment'
		})
		self.assertNotIn('Computer Science', self.client.get('/projects/1/closed/').content.decode())

	def test_project_detail_ticket_closed_does_not_list_in_progress_tickets(self):
		self.login_as_admin()

		self.client.post('/tickets/1/new/', data={
			'title': 'Computer Science',
			'description': 'A department',
			'created_date': timezone.now(),
			'priority': 'low',
			'type': 'comment'
		})
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'low',
			'status': 'in_progress',
			'type': 'comment'
		})

		self.assertNotIn('Computer Science', self.client.get('/projects/1/closed/').content.decode())

	####################################
	# Project detail ticket open tests #
	####################################

	def test_admins_can_view_project_detail_ticket_open(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/projects/1/'), 'projects/project_detail_ticket_open.html')

	def test_project_managers_can_view_project_detail_ticket_open(self):
		self.login_as_project_manager()
		self.assertTemplateUsed(self.client.get('/projects/1/'), 'projects/project_detail_ticket_open.html')

	def test_developers_can_view_project_detail_ticket_open(self):
		self.login_as_developer()
		self.assertTemplateUsed(self.client.get('/projects/1/'), 'projects/project_detail_ticket_open.html')

	def test_users_can_view_project_detail_ticket_open(self):
		self.login_as_user()
		self.assertTemplateUsed(self.client.get('/projects/1/'), 'projects/project_detail_ticket_open.html')

	def test_project_detail_ticket_open_renders_correct_project_information(self):
		self.login_as_admin()

		response = self.client.get('/projects/1/').content.decode()

		self.assertIn('Oxford University', response)
		self.assertIn('University in England', response)
		self.assertIn('MaryMagdalene', response)

	def test_project_detail_ticket_open_lists_open_tickets(self):
		self.login_as_admin()
		self.client.post('/tickets/1/new/', data={
			'title': 'Computer Science',
			'description': 'A department',
			'created_date': timezone.now(),
			'priority': 'low',
			'type': 'comment'
		})
		self.assertIn('Computer Science', self.client.get('/projects/1/').content.decode())

	def test_project_detail_ticket_open_lists_in_progress_tickets(self):
		self.login_as_admin()

		self.client.post('/tickets/1/new/', data={
			'title': 'Computer Science',
			'description': 'A department',
			'created_date': timezone.now(),
			'priority': 'low',
			'type': 'comment'
		})
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'low',
			'status': 'in_progress',
			'type': 'comment'
		})

		self.assertIn('Computer Science', self.client.get('/projects/1/').content.decode())

	def test_project_detail_ticket_open_does_not_list_closed_tickets(self):
		self.login_as_admin()

		self.client.post('/tickets/1/new/', data={
			'title': 'Computer Science',
			'description': 'A department',
			'created_date': timezone.now(),
			'priority': 'low',
			'type': 'comment'
		})
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'low',
			'status': 'closed',
			'type': 'comment'
		})

		self.assertNotIn('Computer Science', self.client.get('/projects/1/').content.decode())

	######################
	# Project edit tests #
	######################

	def test_cannot_edit_archived_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertEqual(404, self.client.post('/projects/1/edit/', data={
			'title': 'University of Oxford',
			'description': 'A university in England',
			'project_manager': Account.objects.get(pk=2).id
		}).status_code)

	def test_admins_can_edit_projects(self):
		self.login_as_admin()

		self.client.post('/projects/1/edit/', data={
			'title': 'University of Oxford',
			'description': 'A university in England',
			'project_manager': Account.objects.get(pk=2).id
		})
		project = Project.objects.get(pk=1)

		self.assertEqual('University of Oxford', project.title)
		self.assertEqual('A university in England', project.description)
		self.assertEqual('LadyMargaret', project.project_manager.user.username)

	def test_project_managers_can_edit_their_projects(self):
		self.login_as_project_manager()

		self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=2).id
		})
		self.client.post('/projects/2/edit/', data={
			'title': 'University of Cambridge',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=2).id
		})
		project = Project.objects.get(pk=2)

		self.assertEqual('University of Cambridge', project.title)
		self.assertEqual('Another university in England', project.description)
		self.assertEqual('LadyMargaret', project.project_manager.user.username)

	def test_project_managers_cannot_edit_other_projects(self):
		self.login_as_project_manager()
		self.assertEqual(404, self.client.get('/projects/1/edit/').status_code)

	def test_developers_cannot_edit_projects(self):
		self.login_as_developer()
		self.assertEqual(404, self.client.post('/projects/1/edit/', data={
			'title': 'University of Oxford',
			'description': 'A university in England',
			'project_manager': Account.objects.get(pk=2).id
		}).status_code)

	def test_users_cannot_edit_projects(self):
		self.login_as_user()
		self.assertEqual(404, self.client.post('/projects/1/edit/', data={
			'title': 'University of Oxford',
			'description': 'A university in England',
			'project_manager': Account.objects.get(pk=2).id
		}).status_code)

	def test_demo_accounts_cannot_edit_projects(self):
		self.login_as_demo()
		self.assertEqual(404, self.client.post('/projects/1/edit/', data={
			'title': 'University of Oxford',
			'description': 'A university in England',
			'project_manager': Account.objects.get(pk=2).id
		}).status_code)

	def test_project_edit_uses_correct_template(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/projects/1/edit/'), 'projects/project_edit.html')

	def test_project_edit_sends_notification_to_old_project_project_manager(self):
		self.login_as_admin()
		self.client.post('/projects/1/edit/', data={
			'title': 'University of Oxford',
			'description': 'A university in England',
			'project_manager': Account.objects.get(pk=2).id
		})
		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=2).recipient.user.username)

	def test_project_edit_sends_notification_to_new_project_project_manager(self):
		self.login_as_admin()
		self.client.post('/projects/1/edit/', data={
			'title': 'University of Oxford',
			'description': 'A university in England',
			'project_manager': Account.objects.get(pk=2).id
		})
		self.assertEqual('LadyMargaret', Notification.objects.get(pk=3).recipient.user.username)

	def test_project_edit_does_not_send_notification_if_project_project_manager_does_not_change(self):
		self.login_as_admin()
		self.client.post('/projects/1/edit/', data={
			'title': 'University of Oxford',
			'description': 'A university in England',
			'project_manager': Account.objects.get(pk=1).id
		})
		self.assertEqual(1, len(Notification.objects.all()))

	def test_project_edit_redirects_after_editing_projects(self):
		self.login_as_admin()

		response = self.client.post('/projects/1/edit/', data={
			'title': 'University of Oxford',
			'description': 'A university in England',
			'project_manager': Account.objects.get(pk=2).id
		})

		self.assertEqual(302, response.status_code)
		self.assertEqual('/projects/1/', response['location'])

	######################
	# Project list tests #
	######################

	def test_admins_can_view_project_list(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/projects/'), 'projects/project_list.html')

	def test_project_managers_can_view_project_list(self):
		self.login_as_project_manager()
		self.assertTemplateUsed(self.client.get('/projects/'), 'projects/project_list.html')

	def test_developers_can_view_project_list(self):
		self.login_as_developer()
		self.assertTemplateUsed(self.client.get('/projects/'), 'projects/project_list.html')

	def test_users_can_view_project_list(self):
		self.login_as_user()
		self.assertTemplateUsed(self.client.get('/projects/'), 'projects/project_list.html')

	def test_project_list_lists_all_active_projects(self):
		self.login_as_admin()
		self.assertIn('Oxford University', self.client.get('/projects/').content.decode())

	def test_project_list_does_not_list_archived_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertNotIn('Oxford University', self.client.get('/projects/').content.decode())

	#####################
	# Project new tests #
	#####################

	def test_admins_can_create_new_projects(self):
		self.login_as_admin()

		self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=1).id
		})
		project = Project.objects.get(title='Cambridge University')

		self.assertEqual('Cambridge University', project.title)
		self.assertEqual('Another university in England', project.description)
		self.assertEqual('MaryMagdalene', project.project_manager.user.username)

	def test_project_managers_can_create_new_projects(self):
		self.login_as_project_manager()

		self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=1).id
		})
		project = Project.objects.get(title='Cambridge University')

		self.assertEqual('Cambridge University', project.title)
		self.assertEqual('Another university in England', project.description)
		self.assertEqual('MaryMagdalene', project.project_manager.user.username)

	def test_developers_cannot_create_new_projects(self):
		self.login_as_developer()
		self.assertEqual(404, self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=1).id
		}).status_code)

	def test_users_cannot_create_new_projects(self):
		self.login_as_user()
		self.assertEqual(404, self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=1).id
		}).status_code)

	def test_demo_accounts_cannot_create_new_projects(self):
		self.login_as_demo()
		self.assertEqual(404, self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=1).id
		}).status_code)

	def test_project_new_uses_correct_template(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/projects/new/'), 'projects/project_new.html')

	def test_project_new_sends_notification_to_project_project_manager(self):
		self.login_as_admin()
		self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=1).id
		})
		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=2).recipient.user.username)

	def test_project_new_redirects_after_creating_new_projects(self):
		self.login_as_admin()

		response = self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=1).id
		})

		self.assertEqual(302, response.status_code)
		self.assertEqual('/projects/2/', response['location'])

	########################
	# Project remove tests #
	########################

	def test_admins_can_remove_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/remove/')
		self.assertFalse(Project.objects.all())

	def test_project_managers_cannot_remove_projects(self):
		self.login_as_project_manager()
		self.assertEqual(404, self.client.get('/projects/1/remove/').status_code)

	def test_developers_cannot_remove_projects(self):
		self.login_as_developer()
		self.assertEqual(404, self.client.get('/projects/1/remove/').status_code)

	def test_users_cannot_remove_projects(self):
		self.login_as_user()
		self.assertEqual(404, self.client.get('/projects/1/remove/').status_code)

	def test_demo_accounts_cannot_remove_projects(self):
		self.login_as_demo()
		self.assertEqual(404, self.client.get('/projects/1/remove/').status_code)

	def test_project_remove_sends_notification_to_project_project_manager(self):
		self.login_as_admin()

		self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=1).id
		})
		self.client.get('/projects/2/remove/')

		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=3).recipient.user.username)

	def test_project_remove_redirects_after_removing_projects(self):
		self.login_as_admin()

		response = self.client.get('/projects/1/remove/')

		self.assertEqual(302, response.status_code)
		self.assertEqual('/projects/', response['location'])

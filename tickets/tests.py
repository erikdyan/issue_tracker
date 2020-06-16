from django.test import TestCase
from django.utils import timezone

from accounts.models import Account
from notifications.models import Notification
from tickets.models import Ticket


class TicketsTest(TestCase):

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

		# Create a project.
		self.login_as_admin()
		self.client.post('/projects/new/', data={
			'title': 'Oxford University',
			'description': 'University in England',
			'project_manager': Account.objects.get(pk=1).id
		})

		# Create a ticket.
		self.client.post('/tickets/1/new/', data={
			'title': 'Computer Science',
			'description': 'A department',
			'created_date': timezone.now(),
			'priority': 'low',
			'type': 'comment'
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

	#######################
	# Assigned list tests #
	#######################

	def test_admins_can_view_ticket_list_assigned(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/tickets/assigned/'), 'tickets/ticket_list_assigned.html')

	def test_project_managers_can_view_ticket_list_assigned(self):
		self.login_as_project_manager()
		self.assertTemplateUsed(self.client.get('/tickets/assigned/'), 'tickets/ticket_list_assigned.html')

	def test_developers_can_view_ticket_list_assigned(self):
		self.login_as_developer()
		self.assertTemplateUsed(self.client.get('/tickets/assigned/'), 'tickets/ticket_list_assigned.html')

	def test_users_cannot_view_ticket_list_assigned(self):
		self.login_as_user()
		self.assertEqual(404, self.client.get('/tickets/assigned/').status_code)

	def test_ticket_list_assigned_lists_tickets_assigned_to_request_user(self):
		self.login_as_admin()
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'low',
			'status': 'open',
			'type': 'comment'
		})
		self.assertIn('Computer Science', self.client.get('/tickets/assigned/').content.decode())

	def test_ticket_list_assigned_does_not_list_tickets_not_assigned_to_request_user(self):
		self.login_as_admin()
		self.assertNotIn('Computer Science', self.client.get('/tickets/assigned/').content.decode())

	######################
	# Created list tests #
	######################

	def test_admins_can_view_ticket_list_created(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/tickets/created/'), 'tickets/ticket_list_created.html')

	def test_project_managers_can_view_ticket_list_created(self):
		self.login_as_project_manager()
		self.assertTemplateUsed(self.client.get('/tickets/created/'), 'tickets/ticket_list_created.html')

	def test_developers_can_view_ticket_list_created(self):
		self.login_as_developer()
		self.assertTemplateUsed(self.client.get('/tickets/created/'), 'tickets/ticket_list_created.html')

	def test_users_can_view_ticket_list_created(self):
		self.login_as_user()
		self.assertTemplateUsed(self.client.get('/tickets/created/'), 'tickets/ticket_list_created.html')

	def test_ticket_list_created_lists_tickets_created_by_request_user(self):
		self.login_as_admin()
		self.assertIn('Computer Science', self.client.get('/tickets/created/').content.decode())

	def test_ticket_list_created_does_not_list_tickets_not_created_by_request_user(self):
		self.login_as_project_manager()
		self.assertNotIn('Computer Science', self.client.get('/tickets/created').content.decode())

	######################
	# Ticket close tests #
	######################

	def test_cannot_close_tickets_in_archived_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertEqual(404, self.client.get('/tickets/1/close/').status_code)

	def test_admins_can_close_tickets(self):
		self.login_as_admin()

		self.client.get('/tickets/1/close/')
		ticket = Ticket.objects.get(pk=1)

		self.assertEqual(None, ticket.assigned_to)
		self.assertEqual('closed', ticket.status)

	def test_project_managers_can_close_tickets_in_their_projects(self):
		self.login_as_project_manager()
		self.client.post('/projects/new/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=2).id
		})
		self.client.post('/tickets/2/new/', data={
			'title': 'Philosophy',
			'description': 'Another department',
			'created_date': timezone.now(),
			'priority': 'high',
			'type': 'feature_request'
		})

		self.client.get('/tickets/2/close/')
		ticket = Ticket.objects.get(pk=2)

		self.assertEqual(None, ticket.assigned_to)
		self.assertEqual('closed', ticket.status)

	def test_project_managers_cannot_close_tickets_not_in_their_projects(self):
		self.login_as_project_manager()
		self.assertEqual(404, self.client.get('/tickets/1/close/').status_code)

	def test_developers_can_close_tickets_they_are_assigned_to(self):
		self.login_as_admin()
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=3).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		self.client.get('/accounts/logout/')
		self.login_as_developer()

		self.client.get('/tickets/1/close/')
		ticket = Ticket.objects.get(pk=1)

		self.assertEqual(None, ticket.assigned_to)
		self.assertEqual('closed', ticket.status)

	def test_developers_cannot_close_tickets_they_are_not_assigned_to(self):
		self.login_as_developer()
		self.assertEqual(404, self.client.get('/tickets/1/close/').status_code)

	def test_users_cannot_close_tickets(self):
		self.login_as_user()
		self.assertEqual(404, self.client.get('/tickets/1/close/').status_code)

	def test_ticket_close_sends_notification_to_ticket_assigned_to(self):
		self.login_as_admin()

		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		self.client.get('/tickets/1/close/')

		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=4).recipient.user.username)

	def test_ticket_close_does_not_send_notification_to_ticket_assigned_to_if_ticket_assigned_to_is_none(self):
		self.login_as_admin()
		self.client.get('/tickets/1/close/')
		self.assertEqual(4, len(Notification.objects.all()))

	def test_ticket_close_sends_notification_to_ticket_author(self):
		self.login_as_admin()
		self.client.get('/tickets/1/close/')
		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=4).recipient.user.username)

	def test_ticket_close_redirects_after_closing_tickets(self):
		self.login_as_admin()

		response = self.client.get('/tickets/1/close/')

		self.assertEqual(302, response.status_code)
		self.assertEqual('/tickets/1/', response['location'])

	#######################
	# Ticket detail tests #
	#######################

	def test_admins_can_view_ticket_detail(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/tickets/1/'), 'tickets/ticket_detail.html')

	def test_project_managers_can_view_ticket_detail(self):
		self.login_as_project_manager()
		self.assertTemplateUsed(self.client.get('/tickets/1/'), 'tickets/ticket_detail.html')

	def test_developers_can_view_ticket_detail(self):
		self.login_as_developer()
		self.assertTemplateUsed(self.client.get('/tickets/1/'), 'tickets/ticket_detail.html')

	def test_users_can_view_ticket_detail(self):
		self.login_as_user()
		self.assertTemplateUsed(self.client.get('/tickets/1/'), 'tickets/ticket_detail.html')

	def test_ticket_detail_renders_correct_information(self):
		self.login_as_admin()

		response = self.client.get('/tickets/1/').content.decode()

		self.assertIn('Computer Science', response)
		self.assertIn('A department', response)
		self.assertIn('Oxford University', response)
		self.assertIn('MaryMagdalene', response)
		self.assertIn('Low', response)
		self.assertIn('Open', response)
		self.assertIn('Comment', response)

	#####################
	# Ticket edit tests #
	#####################

	def test_admins_can_edit_tickets(self):
		self.login_as_admin()

		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		ticket = Ticket.objects.get(pk=1)

		self.assertEqual('high', ticket.priority)
		self.assertEqual('closed', ticket.status)
		self.assertEqual('bug', ticket.type)
		self.assertEqual('MaryMagdalene', ticket.assigned_to.user.username)

	def test_project_managers_can_edit_tickets_in_their_projects(self):
		self.login_as_admin()
		self.client.post('/projects/1/edit/', data={
			'title': 'Cambridge University',
			'description': 'Another university in England',
			'project_manager': Account.objects.get(pk=2).id
		})
		self.client.get('/accounts/logout/')
		self.login_as_project_manager()

		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		ticket = Ticket.objects.get(pk=1)

		self.assertEqual('high', ticket.priority)
		self.assertEqual('closed', ticket.status)
		self.assertEqual('bug', ticket.type)
		self.assertEqual('MaryMagdalene', ticket.assigned_to.user.username)

	def test_project_managers_cannot_edit_tickets_not_in_their_projects(self):
		self.login_as_project_manager()
		self.assertEqual(404, self.client.get('/tickets/1/edit/').status_code)

	def test_developers_can_edit_tickets_they_are_assigned_to(self):
		self.login_as_admin()
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=3).id,
			'priority': 'low',
			'status': 'open',
			'type': 'comment'
		})
		self.client.get('/accounts/logout/')
		self.login_as_developer()

		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		ticket = Ticket.objects.get(pk=1)

		self.assertEqual('high', ticket.priority)
		self.assertEqual('closed', ticket.status)
		self.assertEqual('bug', ticket.type)
		self.assertEqual('MaryMagdalene', ticket.assigned_to.user.username)

	def test_developers_cannot_edit_tickets_they_are_not_assigned_to(self):
		self.login_as_developer()
		self.assertEqual(404, self.client.get('/tickets/1/edit/').status_code)

	def test_users_cannot_edit_tickets(self):
		self.login_as_user()
		self.assertEqual(404, self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		}).status_code)

	def test_cannot_edit_tickets_in_archived_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertEqual(404, self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		}).status_code)

	def test_ticket_edit_uses_correct_template(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/tickets/1/edit/'), 'tickets/ticket_edit.html')

	def test_ticket_edit_sets_updated_date_after_editing_a_ticket(self):
		self.login_as_admin()
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		self.assertIsNotNone(Ticket.objects.get(pk=1).updated_date)

	def test_ticket_edit_sends_notification_to_old_ticket_assigned_to(self):
		self.login_as_admin()

		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=2).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})

		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=5).recipient.user.username)

	def test_ticket_edit_does_not_send_notification_to_old_ticket_assigned_to_if_old_ticket_assigned_to_is_none(self):
		self.login_as_admin()
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		self.assertEqual(4, len(Notification.objects.all()))

	def test_ticket_edit_sends_notification_to_new_ticket_assigned_to(self):
		self.login_as_admin()
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=4).recipient.user.username)

	def test_ticket_edit_does_not_send_notifications_if_ticket_assigned_to_does_not_change(self):
		self.login_as_admin()

		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})

		self.assertEqual(4, len(Notification.objects.all()))

	def test_ticket_edit_redirects_after_editing_tickets(self):
		self.login_as_admin()

		response = self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})

		self.assertEqual(302, response.status_code)
		self.assertEqual('/tickets/1/', response['location'])

	####################
	# Ticket new tests #
	####################

	def test_cannot_create_new_tickets_from_archived_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertEqual(404, self.client.post('/tickets/1/new/', data={
			'title': 'Philosophy',
			'description': 'Another department',
			'created_date': timezone.now(),
			'priority': 'high',
			'type': 'feature_request'
		}).status_code)

	def test_admins_can_create_new_tickets(self):
		self.login_as_admin()

		self.client.post('/tickets/1/new/', data={
			'title': 'Philosophy',
			'description': 'Another department',
			'created_date': timezone.now(),
			'priority': 'high',
			'type': 'feature_request'
		})
		ticket = Ticket.objects.get(title='Philosophy')

		self.assertEqual('Philosophy', ticket.title)
		self.assertEqual('Another department', ticket.description)
		self.assertEqual('MaryMagdalene', ticket.author.user.username)
		self.assertEqual('high', ticket.priority)
		self.assertEqual('open', ticket.status)
		self.assertEqual('feature_request', ticket.type)

	def test_project_managers_can_create_new_tickets(self):
		self.login_as_project_manager()

		self.client.post('/tickets/1/new/', data={
			'title': 'Philosophy',
			'description': 'Another department',
			'created_date': timezone.now(),
			'priority': 'high',
			'type': 'feature_request'
		})
		ticket = Ticket.objects.get(title='Philosophy')

		self.assertEqual('Philosophy', ticket.title)
		self.assertEqual('Another department', ticket.description)
		self.assertEqual('LadyMargaret', ticket.author.user.username)
		self.assertEqual('high', ticket.priority)
		self.assertEqual('open', ticket.status)
		self.assertEqual('feature_request', ticket.type)

	def test_developers_can_create_new_tickets(self):
		self.login_as_developer()

		self.client.post('/tickets/1/new/', data={
			'title': 'Philosophy',
			'description': 'Another department',
			'created_date': timezone.now(),
			'priority': 'high',
			'type': 'feature_request'
		})
		ticket = Ticket.objects.get(title='Philosophy')

		self.assertEqual('Philosophy', ticket.title)
		self.assertEqual('Another department', ticket.description)
		self.assertEqual('PhillipPullman', ticket.author.user.username)
		self.assertEqual('high', ticket.priority)
		self.assertEqual('open', ticket.status)
		self.assertEqual('feature_request', ticket.type)

	def test_users_can_create_new_tickets(self):
		self.login_as_user()

		self.client.post('/tickets/1/new/', data={
			'title': 'Philosophy',
			'description': 'Another department',
			'created_date': timezone.now(),
			'priority': 'high',
			'type': 'feature_request'
		})
		ticket = Ticket.objects.get(title='Philosophy')

		self.assertEqual('Philosophy', ticket.title)
		self.assertEqual('Another department', ticket.description)
		self.assertEqual('J.R.R.Tolkien', ticket.author.user.username)
		self.assertEqual('high', ticket.priority)
		self.assertEqual('open', ticket.status)
		self.assertEqual('feature_request', ticket.type)

	def test_ticket_new_uses_correct_template(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/tickets/1/new/'), 'tickets/ticket_new.html')

	def test_ticket_new_sends_notification_to_ticket_project_project_manager(self):
		self.login_as_admin()
		self.client.post('/tickets/1/new/', data={
			'title': 'Philosophy',
			'description': 'Another department',
			'created_date': timezone.now(),
			'priority': 'high',
			'type': 'feature_request'
		})
		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=5).recipient.user.username)

	def test_ticket_new_sends_notification_to_ticket_author(self):
		self.login_as_admin()
		self.client.post('/tickets/1/new/', data={
			'title': 'Philosophy',
			'description': 'Another department',
			'created_date': timezone.now(),
			'priority': 'high',
			'type': 'feature_request'
		})
		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=4).recipient.user.username)

	def test_ticket_new_redirects_after_creating_new_tickets(self):
		self.login_as_admin()

		response = self.client.post('/tickets/1/new/', data={
			'title': 'Philosophy',
			'description': 'Another department',
			'created_date': timezone.now(),
			'priority': 'high',
			'type': 'feature_request'
		})

		self.assertEqual(302, response.status_code)
		self.assertEqual('/tickets/2/', response['location'])

	#######################
	# Ticket remove tests #
	#######################

	def test_admins_can_remove_tickets(self):
		self.login_as_admin()
		self.client.get('/tickets/1/remove/')
		self.assertFalse(Ticket.objects.all())

	def test_project_managers_cannot_remove_tickets(self):
		self.login_as_project_manager()
		self.assertEqual(404, self.client.get('/tickets/1/remove/').status_code)

	def test_developers_cannot_remove_tickets(self):
		self.login_as_developer()
		self.assertEqual(404, self.client.get('/tickets/1/remove/').status_code)

	def test_users_cannot_remove_tickets(self):
		self.login_as_user()
		self.assertEqual(404, self.client.get('/tickets/1/remove/').status_code)

	def test_cannot_remove_tickets_from_archived_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertEqual(404, self.client.get('/tickets/1/remove/').status_code)

	def test_ticket_remove_sends_notification_to_ticket_assigned_to(self):
		self.login_as_admin()

		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		self.client.get('/tickets/1/remove/')

		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=5).recipient.user.username)

	def test_ticket_remove_redirects_after_removing_tickets(self):
		self.login_as_admin()

		response = self.client.get('/tickets/1/remove/')

		self.assertEqual(302, response.status_code)
		self.assertEqual('/tickets/assigned/', response['location'])

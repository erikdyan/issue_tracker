from django.test import TestCase
from django.utils import timezone

from accounts.models import Account
from comments.models import Comment
from notifications.models import Notification
from tickets.models import Ticket


class CommentsTest(TestCase):

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

		# Create a ticket.
		self.client.post('/tickets/1/new/', data={
			'title': 'Computer Science',
			'description': 'A department',
			'created_date': timezone.now(),
			'priority': 'low',
			'status': 'open',
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

	def login_as_demo(self):
		self.client.post('/accounts/login/', data={'username': 'WilliamMorris', 'password': 'TestPassword'})

	#####################
	# Comment new tests #
	#####################

	def test_cannot_add_new_comment_to_ticket_in_archived_projects(self):
		self.login_as_admin()
		self.client.get('/projects/1/archive/')
		self.assertEqual(404, self.client.post('/comments/1/new/', data={'text': 'Functional Programming'}).status_code)

	def test_admins_can_create_new_comments(self):
		self.login_as_admin()

		self.client.post('/comments/1/new/', data={'text': 'Functional Programming'})
		comment = Comment.objects.get(pk=1)

		self.assertEqual('Functional Programming', comment.text)
		self.assertEqual('MaryMagdalene', comment.author.user.username)
		self.assertEqual(Ticket.objects.get(pk=1), comment.ticket)

	def test_project_managers_can_create_new_comments(self):
		self.login_as_project_manager()

		self.client.post('/comments/1/new/', data={'text': 'Functional Programming'})
		comment = Comment.objects.get(pk=1)

		self.assertEqual('Functional Programming', comment.text)
		self.assertEqual('LadyMargaret', comment.author.user.username)
		self.assertEqual(Ticket.objects.get(pk=1), comment.ticket)

	def test_developers_can_create_new_comments(self):
		self.login_as_developer()

		self.client.post('/comments/1/new/', data={'text': 'Functional Programming'})
		comment = Comment.objects.get(pk=1)

		self.assertEqual('Functional Programming', comment.text)
		self.assertEqual('PhillipPullman', comment.author.user.username)
		self.assertEqual(Ticket.objects.get(pk=1), comment.ticket)

	def test_users_can_create_new_comments(self):
		self.login_as_user()

		self.client.post('/comments/1/new/', data={'text': 'Functional Programming'})
		comment = Comment.objects.get(pk=1)

		self.assertEqual('Functional Programming', comment.text)
		self.assertEqual('J.R.R.Tolkien', comment.author.user.username)
		self.assertEqual(Ticket.objects.get(pk=1), comment.ticket)

	def test_demo_accounts_cannot_create_new_comments(self):
		self.login_as_demo()
		self.assertEqual(404, self.client.post('/comments/1/new/', data={'text': 'Functional Programming'}).status_code)

	def test_comment_new_uses_correct_template(self):
		self.login_as_admin()
		self.assertTemplateUsed(self.client.get('/comments/1/new/'), 'comments/comment_new.html')

	def test_comment_new_sends_notification_to_ticket_assigned_to(self):
		self.login_as_admin()

		self.client.post('/tickets/1/edit/', data={
			'assigned_to': Account.objects.get(pk=1).id,
			'priority': 'high',
			'status': 'closed',
			'type': 'bug'
		})
		self.client.post('/comments/1/new/', data={'text': 'Functional Programming'})

		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=5).recipient.user.username)

	def test_comment_new_does_not_send_notification_to_ticket_assigned_to_if_ticket_assigned_to_is_none(self):
		self.login_as_admin()
		self.client.post('/comments/1/new/', data={'text': 'Functional Programming'})
		self.assertEqual(4, len(Notification.objects.all()))

	def test_comment_new_sends_notification_to_ticket_author(self):
		self.login_as_admin()
		self.client.post('/comments/1/new/', data={'text': 'Functional Programming'})
		self.assertEqual('MaryMagdalene', Notification.objects.get(pk=4).recipient.user.username)

	def test_comment_new_redirects_after_creating_new_comments(self):
		self.login_as_admin()

		response = self.client.post('/comments/1/new/', data={'text': 'Functional Programming'})

		self.assertEqual(302, response.status_code)
		self.assertEqual('/tickets/1/', response['location'])

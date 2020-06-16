from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from projects.models import Project
from tickets.models import Ticket


@login_required
def index(request):
	return render(request, 'index/index.html', {
		'assigned_to_all': Ticket.objects.filter(assigned_to=request.user.account),
		'assigned_to_open': (
				Ticket.objects.filter(assigned_to=request.user.account) &
				Ticket.objects.filter(status='open')
		),
		'assigned_to_in_progress': (
				Ticket.objects.filter(assigned_to=request.user.account) &
				Ticket.objects.filter(status='in_progress')
		),
		'assigned_to_closed': (
				Ticket.objects.filter(assigned_to=request.user.account) &
				Ticket.objects.filter(status='closed')
		),
		'assigned_to_bug': (
				Ticket.objects.filter(assigned_to=request.user.account) &
				Ticket.objects.filter(type='bug')
		),
		'assigned_to_feature_request': (
				Ticket.objects.filter(assigned_to=request.user.account) &
				Ticket.objects.filter(type='feature_request')
		),
		'assigned_to_comment': (
				Ticket.objects.filter(assigned_to=request.user.account) &
				Ticket.objects.filter(type='comment')
		),
		'created_by_all': Ticket.objects.filter(author=request.user.account),
		'created_by_open': (
				Ticket.objects.filter(author=request.user.account) &
				Ticket.objects.filter(status='open')
		),
		'created_by_in_progress': (
				Ticket.objects.filter(author=request.user.account) &
				Ticket.objects.filter(status='in_progress')
		),
		'created_by_closed': (
				Ticket.objects.filter(author=request.user.account) &
				Ticket.objects.filter(status='closed')
		),
		'created_by_bug': (
				Ticket.objects.filter(author=request.user.account) &
				Ticket.objects.filter(type='bug')
		),
		'created_by_feature_request': (
				Ticket.objects.filter(author=request.user.account) &
				Ticket.objects.filter(type='feature_request')
		),
		'created_by_comment': (
				Ticket.objects.filter(author=request.user.account) &
				Ticket.objects.filter(type='comment')
		),
		'unassigned_tickets': (
				Ticket.objects.filter(assigned_to=None) &
				Ticket.objects.filter(project__project_manager=request.user.account)),
		'top_projects': Project.objects.filter(archived=False).annotate(num_tickets=Count('tickets')).
				  order_by('-num_tickets')[:3],
		'more_projects': Project.objects.filter(archived=False).annotate(num_tickets=Count('tickets')).
				  order_by('-num_tickets')[3:10]
	})

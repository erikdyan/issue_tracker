from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import Notification
from projects.models import Project
from tickets.forms import EditTicketForm, NewTicketForm
from tickets.models import Ticket


@login_required
def ticket_close(request, pk):
	ticket = get_object_or_404(Ticket, pk=pk)
	if ticket.project.archived:
		raise Http404
	elif request.user.account.role == 'project_manager' and request.user.account != ticket.project.project_manager:
		raise Http404
	elif request.user.account.role == 'developer' and request.user.account != ticket.assigned_to:
		raise Http404
	elif request.user.account.role == 'user':
		raise Http404

	assigned_to = ticket.assigned_to
	ticket.close()

	if assigned_to is not None:
		Notification.objects.create(
			title='Ticket Closed',
			text=f'The ticket "{ticket.title}" has been closed.',
			recipient=assigned_to
		)

	Notification.objects.create(
		title='Ticket Closed',
		text=f'The ticket "{ticket.title}" has been closed.',
		recipient=ticket.author
	)

	return redirect('ticket_detail', pk)


@login_required
def ticket_detail(request, pk):
	return render(request, 'tickets/ticket_detail.html', {'ticket': get_object_or_404(Ticket, pk=pk)})


@login_required
def ticket_edit(request, pk):
	ticket = get_object_or_404(Ticket, pk=pk)
	if ticket.project.archived:
		raise Http404
	elif request.user.account.role == 'project_manager' and request.user.account != ticket.project.project_manager:
		raise Http404
	elif request.user.account.role == 'developer' and request.user.account != ticket.assigned_to:
		raise Http404
	elif request.user.account.role == 'user':
		raise Http404

	assigned_to = ticket.assigned_to
	title = ticket.title

	if request.method == 'POST':
		form = EditTicketForm(request.POST, instance=ticket)
		if form.is_valid():
			ticket = form.save()
			ticket.update()

			if not assigned_to == ticket.assigned_to:
				if assigned_to is not None:
					Notification.objects.create(
						title='Ticket Edited',
						text=f'You have been unassigned from "{title}".',
						recipient=assigned_to
					)
				Notification.objects.create(
					title='Ticket Edited',
					text=f'You have been assigned to "{title}".',
					recipient=ticket.assigned_to
				)

			return redirect('ticket_detail', pk)

	return render(request, 'tickets/ticket_edit.html', {'form': EditTicketForm(instance=ticket), 'ticket': ticket})


@login_required
def ticket_list_assigned(request):
	if request.user.account.role == 'user':
		raise Http404

	return render(request, 'tickets/ticket_list_assigned.html', {
		'tickets': Ticket.objects.filter(assigned_to=request.user.account).order_by('status').reverse()
	})


@login_required
def ticket_list_created(request):
	return render(request, 'tickets/ticket_list_created.html', {
		'tickets': Ticket.objects.filter(author=request.user.account).order_by('status').reverse()
	})


@login_required
def ticket_new(request, pk):
	project = get_object_or_404(Project, pk=pk)
	if project.archived:
		raise Http404

	if request.method == 'POST':
		form = NewTicketForm(request.POST)
		if form.is_valid():
			ticket = form.save(commit=False)
			ticket.author = request.user.account
			ticket.project = project
			ticket.save()

			Notification.objects.create(
				title='New Ticket',
				text=f'Your ticket "{ticket.title}" has been created.',
				recipient=ticket.author
			)
			Notification.objects.create(
				title='New Ticket',
				text=f'Your project "{project.title}" has a new ticket: {ticket.title}.',
				recipient=ticket.project.project_manager
			)

			return redirect('ticket_detail', ticket.pk)

	return render(request, 'tickets/ticket_new.html', {'form': NewTicketForm(), 'project': project})


@login_required
def ticket_remove(request, pk):
	ticket = get_object_or_404(Ticket, pk=pk)
	assigned_to = ticket.assigned_to
	title = ticket.title

	if not request.user.account.role == 'admin' or ticket.project.archived:
		raise Http404

	ticket.delete()

	if assigned_to is not None:
		Notification.objects.create(
			title='Ticket Removed',
			text=f'The ticket "{title}" has been removed.',
			recipient=assigned_to
		)

	return redirect('ticket_list_assigned')

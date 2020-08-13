from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from comments.forms import CommentForm
from notifications.models import Notification
from tickets.models import Ticket


@login_required
def comment_new(request, pk):
	if request.user.account.demo:
		raise Http404
	
	ticket = get_object_or_404(Ticket, pk=pk)
	if ticket.project.archived:
		raise Http404

	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.author = request.user.account
			comment.ticket = ticket
			comment.save()

			assigned_to = ticket.assigned_to
			if assigned_to is not None:
				Notification.objects.create(
					title='New Comment on Your Ticket',
					text=f'The ticket "{ticket.title}" you are assigned to has a new comment.',
					recipient=assigned_to
				)
			Notification.objects.create(
				title='New Comment on Your Ticket',
				text=f'The ticket "{ticket.title}" you created has a new comment.',
				recipient=ticket.author
			)

			return redirect('ticket_detail', ticket.pk)

	return render(request, 'comments/comment_new.html', {'form': CommentForm(), 'ticket': ticket})

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from notifications.models import Notification


@login_required
def notification_detail(request, pk):
	notification = get_object_or_404(Notification, pk=pk)
	if not request.user.account == notification.recipient:
		raise Http404

	if not request.user.account.demo:
		notification.mark_read()

	return render(request, 'notifications/notification_detail.html', {'notification': notification})


@login_required
def notification_list(request):
	return render(request, 'notifications/notification_list.html', {
		'notifications': Notification.objects.filter(recipient=request.user.account).order_by('created_date').reverse()
	})

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import Notification
from projects.forms import ProjectForm
from projects.models import Project


@login_required
def project_archive(request, pk):
	if request.user.account.demo:
		raise Http404

	project = get_object_or_404(Project, pk=pk)
	project_manager = project.project_manager

	if not (request.user.account.role == 'admin' or request.user.account.role == 'project_manager'):
		raise Http404
	elif request.user.account.role == 'project_manager' and request.user.account != project_manager:
		raise Http404

	project.archive()

	Notification.objects.create(
		title=f'Project Archived',
		text=f'The project "{project.title}" has been archived. You have been removed as project manager.',
		recipient=project_manager
	)

	return redirect('project_detail_ticket_open', pk)


@login_required
def project_archive_list(request):
	return render(request, 'projects/project_archive_list.html', {'projects': Project.objects.filter(archived=True)})


@login_required
def project_detail_ticket_closed(request, pk):
	project = get_object_or_404(Project, pk=pk)
	return render(request, 'projects/project_detail_ticket_closed.html', {
		'project': project,
		'tickets': project.tickets.filter(status='closed')
	})


@login_required
def project_detail_ticket_open(request, pk):
	project = get_object_or_404(Project, pk=pk)
	return render(request, 'projects/project_detail_ticket_open.html', {
		'project': project,
		'tickets': project.tickets.filter(status='open') | project.tickets.filter(status='in_progress')
	})


@login_required
def project_edit(request, pk):
	if request.user.account.demo:
		raise Http404

	project = get_object_or_404(Project, pk=pk)
	project_manager = project.project_manager

	if project.archived:
		raise Http404
	elif not (request.user.account.role == 'admin' or request.user.account.role == 'project_manager'):
		raise Http404
	elif request.user.account.role == 'project_manager' and request.user.account != project_manager:
		raise Http404

	if request.method == 'POST':
		form = ProjectForm(request.POST, instance=project)
		if form.is_valid():
			new_project_manager = form.save().project_manager
			if not project_manager == new_project_manager:
				Notification.objects.create(
					title=f'Project Edited',
					text=f'You have been removed as project manager from "{project.title}"',
					recipient=project_manager
				)
				Notification.objects.create(
					title=f'Project Edited',
					text=f'You have been appointed as project manager for "{project.title}"',
					recipient=new_project_manager
				)

			return redirect('project_detail_ticket_open', pk)

	return render(request, 'projects/project_edit.html', {'form': ProjectForm(instance=project)})


@login_required
def project_list(request):
	return render(request, 'projects/project_list.html', {'projects': Project.objects.filter(archived=False)})


@login_required
def project_new(request):
	if not (request.user.account.role == 'admin' or request.user.account.role == 'project_manager') or \
			request.user.account.demo:
		raise Http404

	if request.method == 'POST':
		form = ProjectForm(request.POST)
		if form.is_valid():
			project = form.save()
			project_manager = project.project_manager

			Notification.objects.create(
				title=f'Project Created',
				text=f'The project "{project.title}" has been created. You have been appointed as project manager.',
				recipient=project_manager
			)

			return redirect('project_detail_ticket_open', project.pk)

	return render(request, 'projects/project_new.html', {'form': ProjectForm()})


@login_required
def project_remove(request, pk):
	if not request.user.account.role == 'admin' or request.user.account.demo:
		raise Http404

	project = get_object_or_404(Project, pk=pk)
	title = project.title
	project_manager = project.project_manager

	project.delete()

	Notification.objects.create(
		title=f'Project Removed',
		text=f'The project "{title}" has been removed. You have been removed as project manager.',
		recipient=project_manager
	)

	return redirect('project_list')

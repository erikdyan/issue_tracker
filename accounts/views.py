from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import AccountForm, EditUserForm, LoginForm, UserForm
from accounts.models import Account


@login_required
def account_detail(request, pk):
	if not (request.user.account.pk == pk or request.user.account.role == 'admin'):
		raise Http404

	return render(request, 'accounts/account_detail.html', {'account': get_object_or_404(Account, pk=pk)})


@login_required
def account_edit(request, pk):
	if not (request.user.account.pk == pk or request.user.account.role == 'admin'):
		raise Http404

	account = get_object_or_404(Account, pk=pk)

	if request.method == 'POST':

		if not request.user.account.pk == pk:
			account_form = AccountForm(request.POST, instance=account)
			if account_form.is_valid():
				account_form.save()
				return redirect('account_detail', pk)

		elif not request.user.account.role == 'admin':
			user_form = EditUserForm(request.POST, instance=account.user)
			if user_form.is_valid():
				user_form.save()
				return redirect('account_detail', pk)
			else:
				messages.info(request, user_form.errors)
				return redirect('account_edit', pk)

		else:
			account_form = AccountForm(request.POST, instance=account)
			user_form = EditUserForm(request.POST, instance=account.user)
			if account_form.is_valid() and user_form.is_valid():
				account_form.save()
				user_form.save()
				return redirect('account_detail', pk)
			else:
				messages.info(request, user_form.errors)
				return redirect('account_edit', pk)

	account_form = AccountForm(instance=account)
	user_form = EditUserForm(instance=account.user)

	if not request.user.account.pk == pk:
		return render(request, 'accounts/account_edit_role.html', {'account': account, 'form': account_form})

	elif not request.user.account.role == 'admin':
		return render(request, 'accounts/account_edit_user.html', {'account': account, 'form': user_form})

	return render(request, 'accounts/account_edit_admin.html', {'account_form': account_form, 'user_form': user_form})


@login_required
def account_list(request):
	if not request.user.account.role == 'admin':
		raise Http404

	return render(request, 'accounts/account_list.html', {'accounts': Account.objects.all()})


def login(request):
	if request.user.is_authenticated:
		return redirect('index')

	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = auth.authenticate(
				username=form.cleaned_data.get('username'),
				password=form.cleaned_data.get('password')
			)
			if user:
				auth.login(request, user)
				return redirect('index')
			else:
				messages.info(request, 'Incorrect username or password.')
				return redirect('login')

	return render(request, 'accounts/login.html', {'form': LoginForm()})


@login_required
def logout(request):
	auth.logout(request)
	return redirect('login')


@login_required
def my_password_change(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			messages.info(request, 'Password successfully changed.')
			return redirect('account_detail', request.user.account.pk)
		else:
			messages.info(request, form.errors)
			return redirect('my_password_change')

	return render(request, 'accounts/password_change.html', {
		'account': request.user.account,
		'form': PasswordChangeForm(request.user)
	})


def signup(request):
	if request.user.is_authenticated:
		return redirect('index')

	if request.method == 'POST':
		account_form = AccountForm(request.POST)
		user_form = UserForm(request.POST)
		if account_form.is_valid() and user_form.is_valid():
			account = account_form.save(commit=False)
			account.user = user_form.save()
			account.save()
			messages.info(request, 'Signup successful. Please log in.')
			return redirect('login')
		else:
			messages.info(request, user_form.errors)

	return render(request, 'accounts/signup.html', {'account_form': AccountForm(), 'user_form': UserForm()})

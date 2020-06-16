from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views

urlpatterns = [
	path('', views.account_list, name='account_list'),
	path('<int:pk>/', views.account_detail, name='account_detail'),
	path('<int:pk>/edit/', views.account_edit, name='account_edit'),
	path('login/', views.login, name='login'),
	path('logout/', views.logout, name='logout'),
	path('password_change/', views.my_password_change, name='my_password_change'),
	path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
	path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
	path('password_reset/confirm/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
	path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
	path('signup/', views.signup, name='signup')
]

from django.urls import path

from tickets import views

urlpatterns = [
	path('assigned/', views.ticket_list_assigned, name='ticket_list_assigned'),
	path('created/', views.ticket_list_created, name='ticket_list_created'),
	path('<int:pk>/', views.ticket_detail, name='ticket_detail'),
	path('<int:pk>/close/', views.ticket_close, name='ticket_close'),
	path('<int:pk>/edit/', views.ticket_edit, name='ticket_edit'),
	path('<int:pk>/new/', views.ticket_new, name='ticket_new'),
	path('<int:pk>/remove/', views.ticket_remove, name='ticket_remove')
]

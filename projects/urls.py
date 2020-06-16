from django.urls import path

from projects import views

urlpatterns = [
	path('', views.project_list, name='project_list'),
	path('<int:pk>/', views.project_detail_ticket_open, name='project_detail_ticket_open'),
	path('<int:pk>/archive/', views.project_archive, name='project_archive'),
	path('<int:pk>/closed/', views.project_detail_ticket_closed, name='project_detail_ticket_closed'),
	path('<int:pk>/edit/', views.project_edit, name='project_edit'),
	path('<int:pk>/remove/', views.project_remove, name='project_remove'),
	path('archive/', views.project_archive_list, name='project_archive_list'),
	path('new/', views.project_new, name='project_new')
]

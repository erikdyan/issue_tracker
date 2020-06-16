from django.urls import path

from notifications import views

urlpatterns = [
	path('', views.notification_list, name='notification_list'),
	path('<int:pk>/', views.notification_detail, name='notification_detail')
]

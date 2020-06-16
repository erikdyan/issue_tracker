from django.urls import path

from comments import views

urlpatterns = [path('<int:pk>/new/', views.comment_new, name='comment_new')]

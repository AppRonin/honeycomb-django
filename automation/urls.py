from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('gpon-conversor', views.gpon_conversor, name='gpon_conversor'),

    # Celery
    path("start/", views.start_task, name="start-task"),
    path("progress/<task_id>/", views.get_progress, name="task-progress"),
]
from django.urls import path
from candidate import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='candidate-dashboard'),
    path('jobs/', views.jobs_view, name='candidate-jobs'),
    path('jobs/<int:job_id>/resumes/', views.resumes_view, name='candidate-resumes'),
    path('jobs/<int:job_id>/screen/<int:id>/', views.screen_single, name='candidate-screen_single'),
]
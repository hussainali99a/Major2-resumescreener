from django.urls import path
from recruiter import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('jobs/', views.jobs_view, name='jobs'),
    path('jobs/<int:id>/', views.job_detail_api),
    path('candidates/', views.candidates_view, name='candidates'),
    path('candidates/<int:id>/', views.candidate_detail_api),
]
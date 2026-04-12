from django.urls import path
from recruiter import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('jobs/', views.jobs_view, name='jobs'),
    path('jobs/<int:job_id>/', views.job_detail_api),
    path('jobs/<int:job_id>/candidates/', views.candidates_view, name='candidates'),
    path('candidates/<int:id>/', views.candidate_detail_api),
    path('jobs/<int:job_id>/screen/<int:id>/', views.screen_single, name='screen_single'),
    path('jobs/<int:job_id>/screen-all/', views.screen_all, name='screen_all'),
    path('jobs/<int:job_id>/candidates-api/', views.job_candidates_api),
]
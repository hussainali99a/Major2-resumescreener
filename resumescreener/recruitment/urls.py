from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/jobs/', views.jobs_view, name='jobs'),
    path('candidates/', views.candidates_view, name='candidates'),
    path('candidate/<int:id>/', views.candidate_detail_api),
    path('job/<int:id>/', views.job_detail_api),

    path('dashboard/', views.dashboard, name='dashboard'),
]
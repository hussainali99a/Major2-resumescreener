from django.urls import path
from accounts import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path("verify/", views.verify_otp_view, name="verify_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
]
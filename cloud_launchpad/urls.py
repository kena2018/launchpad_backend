from django.urls import path, include
from . import views

urlpatterns = [
    # path('validate', LaunchpadView.as_view()),
    path('validate', views.LaunchpadView.as_view(), name='launchpad_view'),
    path('user_details', views.UserDetailsAPIView.as_view()),
    # path('users/', views.create_user, name='create_user'),
    path('user', views.UserAPIView.as_view()),
    path('login', views.LoginAPIView.as_view()),
    path('company', views.CompanyAPIView.as_view()),
    path('project_details/',views.ProjectDetailsAPIView.as_view()),
    path('forgot_password/',views.ForgotPasswordView.as_view()),
    path('reset_password/',views.ResetPasswordView.as_view())
]
from django.urls import path

from . import views

# define the app name
app_name = 'users'

# url patterns
urlpatterns = [
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/logout', views.LogoutView.as_view(), name='logout'),
    path('auth/validate', views.IsLoggedInView.as_view(), name='validate'),
]

from django.urls import path
from .views import RegisterView, LoginView, LogoutView
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView, name='register'),
    path('login/', LoginView, name='login'),
    path('logout/', LogoutView, name='logout'),
]
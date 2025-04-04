from django.urls import path
from . import views


app_name = 'profiles'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:username>/', views.profile, name='profile'),
]
"""
URL configuration for the Profiles app.
- '' → Calls the index view and lists all profiles.
- '<str:username>/' → Calls the profile view for a specific profile by username.
"""

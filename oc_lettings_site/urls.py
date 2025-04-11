from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('lettings/', include('lettings.urls', namespace='lettings')),
    path('profiles/', include('profiles.urls', namespace='profiles')),
    path('admin/', admin.site.urls),
]
"""
URL configuration for the main app.
- '' → Calls the index view and
- 'lettings/' → Calls the lettings view and lists all lettings.
- 'profiles/' → Calls the profiles view and lists all profiles.
- 'admin/' → Calls the admin view.
"""

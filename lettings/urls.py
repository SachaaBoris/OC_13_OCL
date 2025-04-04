from django.urls import path
from . import views


app_name = 'lettings'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:letting_id>/', views.letting, name='letting'),
]
"""
URL configuration for the Lettings app.
- '' → Calls the index view and lists all lettings.
- '<int:letting_id>/' → Calls the letting view for a specific letting by ID.
"""

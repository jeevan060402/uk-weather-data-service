from django.urls import path
from web_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('explorer/', views.data_explorer, name='data_explorer'),
    path('api/stats/', views.stats_api, name='stats_api'),
]
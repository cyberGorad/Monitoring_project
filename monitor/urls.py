from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('ids', views.dashboard, name='dashboard'),
    path('multi-monitoring', views.monitoring, name = 'multi'),
    path('settings', views.setting, name = 'setting'),
    path('logout', views.user_logout, name ='logout'),
    path('', views.index , name = 'index'),
]

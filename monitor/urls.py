from django.urls import path
from . import views

urlpatterns = [
    path('/ids', views.dashboard, name='dashboard'),
    path('/multi-monitoring', views.monitoring, name = 'multi'),
    path('', views.index , name = 'index'),
]

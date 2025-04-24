from django.urls import path
from . import views

urlpatterns = [
    path('', views.log, name='log'),
]

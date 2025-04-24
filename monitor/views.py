from django.shortcuts import render

def dashboard(request):
    return render(request, 'monitor/dashboard.html')

def monitoring(request):
    return render(request, 'monitor/multi-monitoring.html')

def index(request):
    return render(request, 'monitor/index.html')

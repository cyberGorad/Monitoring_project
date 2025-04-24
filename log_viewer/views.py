from django.shortcuts import render


def log(request):
    return render(request , 'log_viewer/log.html')
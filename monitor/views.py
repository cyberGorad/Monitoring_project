from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm






def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Connexion réussie.")
                return redirect('index')  # redirige après login
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()

    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'monitor/index.html', {
        'username': username,
        'form': form
    })

def user_logout(request):
    logout(request)
    messages.success(request, "Logout success")
    return redirect('index')  # ou une autre page d'accueil


def dashboard(request):
    return render(request, 'monitor/dashboard.html')

def monitoring(request):
    return render(request, 'monitor/multi-monitoring.html')

def setting(request):
    return render(request, 'monitor/settings.html')

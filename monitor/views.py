from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authentifier l'utilisateur
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Connexion réussie")
                return redirect('home')  # Redirige vers la page d'accueil ou autre page protégée
            else:
                messages.error(request, "Identifiants invalides")
        else:
            messages.error(request, "Erreur dans le formulaire")
    else:
        form = AuthenticationForm()

    return render(request, 'monitor/login.html', {'form': form})

def index(request):
    username = request.user.username
    return render(request, 'monitor/index.html',{'username': username})


def dashboard(request):
    return render(request, 'monitor/dashboard.html')

def monitoring(request):
    return render(request, 'monitor/multi-monitoring.html')

def setting(request):
    return render(request, 'monitor/settings.html')

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='Nom d’utilisateur', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')

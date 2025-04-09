from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.error(request, 'As senhas não conferem')
            return redirect('cadastro')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe')
            return redirect('cadastro')
        
        if len(senha) < 8:
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres')
            return redirect('cadastro')
        
        if not username.isalnum():
            messages.error(request, 'O nome de usuário deve conter apenas letras e números')
            return redirect('cadastro')
        
        user = User.objects.create_user(username=username, password=senha)
        user.save()
        messages.success(request, 'Usuário criado com sucesso')
        return redirect('login')
    
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)
        
        if user is None:
            messages.error(request, 'Usuário ou senha inválidos')
            return redirect('login')
        else:
            auth.login(request, user)
            return redirect('mentorados')
        
def logout(request):
    auth.logout(request)
    return redirect('home')
        


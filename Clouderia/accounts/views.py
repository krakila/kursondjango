from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:  # Если пользователь уже вошел, перенаправляем на главную
        return redirect('main_page')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main_page')  # Перенаправляем на главную страницу после входа
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def register(request):
    if request.user.is_authenticated:  # Если пользователь уже вошел, перенаправляем на главную
        return redirect('main_page')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('main_page')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
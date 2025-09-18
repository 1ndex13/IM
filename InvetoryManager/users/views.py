from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomUserCreationForm


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
            return redirect('users:home')
        else:
            messages.error(request, 'Неверный email или пароль')

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('users:login')


@login_required
@user_passes_test(is_admin)
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Пользователь {user.email} успешно создан!')
            return redirect('users:home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def home_view(request):
    return render(request, 'users/home.html', {'user': request.user})
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import models
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from products.models import Product, StockTransaction, PurchaseInvoice

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
    products_count = Product.objects.count()
    low_stock_count = Product.objects.filter(quantity__lte=models.F('min_stock')).count()
    invoices_count = PurchaseInvoice.objects.count()
    recent_transactions = StockTransaction.objects.select_related('product', 'user').order_by('-date')[:5]
    context = {
        'user': request.user,
        'products_count': products_count,
        'low_stock_count': low_stock_count,
        'invoices_count': invoices_count,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'users/home.html', context)




class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
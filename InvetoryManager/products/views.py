from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, StockTransaction
from .forms import ProductForm, StockTransactionForm
from users.views import is_admin


def is_admin_or_manager(user):
    return user.is_authenticated and user.role in ['admin', 'manager']


@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


@login_required
@user_passes_test(is_admin_or_manager)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'Товар успешно создан!')
            return redirect('products:list')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {'form': form, 'title': 'Создать товар'})


@login_required
@user_passes_test(is_admin_or_manager)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлен!')
            return redirect('products:list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {'form': form, 'title': 'Редактировать товар'})


@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удален!')
        return redirect('products:list')

    return render(request, 'products/product_confirm_delete.html', {'product': product})


@login_required
@user_passes_test(is_admin_or_manager)
def stock_transaction(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user

            product = transaction.product
            if transaction.transaction_type == 'in':
                product.quantity += transaction.quantity
            else:
                if product.quantity >= transaction.quantity:
                    product.quantity -= transaction.quantity
                else:
                    messages.error(request, 'Недостаточно товара на складе')
                    return render(request, 'products/stock_transaction.html', {'form': form})

            product.save()
            transaction.save()

            messages.success(request, 'Операция успешно выполнена!')
            return redirect('products:list')
    else:
        form = StockTransactionForm()

    return render(request, 'products/stock_transaction.html', {'form': form})


@login_required
def transaction_history(request):
    transactions = StockTransaction.objects.all().select_related('product', 'user')
    return render(request, 'products/transaction_history.html', {'transactions': transactions})
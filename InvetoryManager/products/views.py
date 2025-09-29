from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Product, StockTransaction, Category, Supplier, PurchaseInvoice, PurchaseInvoiceItem
from .forms import ProductForm, StockTransactionForm, CategoryForm, SupplierForm, PurchaseInvoiceForm, PurchaseInvoiceItemFormSet

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_admin_or_manager(user):
    return user.is_authenticated and user.role in ['admin', 'manager']


@login_required
def product_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    low_stock_filter = request.GET.get('low_stock', '')

    products = Product.objects.all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    if low_stock_filter:
        products = products.filter(quantity__lte=models.F('min_stock'))

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'products': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'low_stock_filter': low_stock_filter,
    }

    return render(request, 'products/product_list.html', context)


@login_required
@user_passes_test(is_admin_or_manager)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
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
        form = ProductForm(request.POST, request.FILES, instance=product)
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


@login_required
@user_passes_test(is_admin_or_manager)
def supplier_list(request):
    """Список поставщиков"""
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'products/supplier_list.html', {'suppliers': suppliers})


@login_required
@user_passes_test(is_admin_or_manager)
def supplier_create(request):
    """Создание поставщика"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Поставщик успешно создан!')
            return redirect('products:supplier_list')
    else:
        form = SupplierForm()

    return render(request, 'products/supplier_form.html', {
        'form': form,
        'title': 'Создать поставщика'
    })


@login_required
@user_passes_test(is_admin_or_manager)
def purchase_invoice_list(request):
    """Список накладных прихода"""
    invoices = PurchaseInvoice.objects.all().select_related('supplier', 'created_by')
    return render(request, 'products/purchase_invoice_list.html', {'invoices': invoices})


@login_required
@user_passes_test(is_admin_or_manager)
def purchase_invoice_create(request):
    """Создание накладной прихода"""
    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST)
        formset = PurchaseInvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    invoice = form.save(commit=False)
                    invoice.created_by = request.user
                    invoice.save()

                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.invoice = invoice
                        instance.save()


                    for instance in formset.deleted_objects:
                        instance.delete()

                messages.success(request, 'Накладная прихода успешно создана!')
                return redirect('products:purchase_invoice_list')

            except Exception as e:
                messages.error(request, f'Ошибка при создании накладной: {str(e)}')
    else:

        last_invoice = PurchaseInvoice.objects.order_by('-id').first()
        next_number = f"ПР-{(last_invoice.id + 1) if last_invoice else 1:06d}" if last_invoice else "ПР-000001"

        form = PurchaseInvoiceForm(initial={'invoice_number': next_number})
        formset = PurchaseInvoiceItemFormSet()

    return render(request, 'products/purchase_invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Создать накладную прихода'
    })


@login_required
@user_passes_test(is_admin_or_manager)
def purchase_invoice_detail(request, pk):
    """Просмотр деталей накладной"""
    invoice = get_object_or_404(PurchaseInvoice.objects.prefetch_related('purchaseinvoiceitem_set__product'), pk=pk)
    items = invoice.purchaseinvoiceitem_set.all()

    return render(request, 'products/purchase_invoice_detail.html', {
        'invoice': invoice,
        'items': items
    })


@login_required
@user_passes_test(is_admin_or_manager)
def purchase_invoice_complete(request, pk):
    """Завершение накладной - увеличение остатков"""
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)

    if invoice.status != 'draft':
        messages.error(request, 'Накладная уже обработана или отменена!')
        return redirect('products:purchase_invoice_detail', pk=pk)

    try:
        with transaction.atomic():

            for item in invoice.purchaseinvoiceitem_set.all():
                product = item.product
                product.quantity += item.quantity
                product.save()

                StockTransaction.objects.create(
                    product=product,
                    transaction_type='in',
                    quantity=item.quantity,
                    user=request.user,
                    comment=f'Приход по накладной {invoice.invoice_number}'
                )

            invoice.status = 'completed'
            invoice.save()

        messages.success(request, 'Накладная успешно завершена! Остатки обновлены.')

    except Exception as e:
        messages.error(request, f'Ошибка при завершении накладной: {str(e)}')

    return redirect('products:purchase_invoice_detail', pk=pk)


@login_required
@user_passes_test(is_admin_or_manager)
def purchase_invoice_cancel(request, pk):
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)

    if invoice.status != 'draft':
        messages.error(request, 'Можно отменять только черновики!')
        return redirect('products:purchase_invoice_detail', pk=pk)

    invoice.status = 'cancelled'
    invoice.save()

    messages.success(request, 'Накладная отменена!')
    return redirect('products:purchase_invoice_detail', pk=pk)


@login_required
def transaction_history(request):
    product_filter = request.GET.get('product', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    user_filter = request.GET.get('user', '')
    transaction_type = request.GET.get('type', '')

    transactions = StockTransaction.objects.all().select_related('product', 'user')

    if product_filter:
        transactions = transactions.filter(product_id=product_filter)

    if date_from:
        transactions = transactions.filter(date__gte=date_from)

    if date_to:
        transactions = transactions.filter(date__lte=date_to)

    if user_filter:
        transactions = transactions.filter(user_id=user_filter)

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    products = Product.objects.all()
    users = get_user_model().objects.filter(stocktransaction__isnull=False).distinct()

    context = {
        'transactions': page_obj,
        'products': products,
        'users': users,
        'product_filter': product_filter,
        'date_from': date_from,
        'date_to': date_to,
        'user_filter': user_filter,
        'transaction_type': transaction_type,
    }

    return render(request, 'products/transaction_history.html', context)
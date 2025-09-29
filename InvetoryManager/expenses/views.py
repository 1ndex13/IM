import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ExpenseInvoice, ExpenseInvoiceItem, ExpenseReason
from .forms import ExpenseInvoiceForm, ExpenseInvoiceItemFormSet, ExpenseReasonForm
from products.models import StockTransaction, Product
from django.contrib.auth import get_user_model

User = get_user_model()


def is_admin_or_manager(user):
    return user.is_authenticated and user.role in ['admin', 'manager']


@login_required
@user_passes_test(is_admin_or_manager)
def expense_reason_list(request):
    """Список причин расхода"""
    reasons = ExpenseReason.objects.all().order_by('name')
    return render(request, 'expenses/expense_reason_list.html', {'reasons': reasons})


@login_required
@user_passes_test(is_admin_or_manager)
def expense_reason_create(request):
    """Создание причины расхода"""
    if request.method == 'POST':
        form = ExpenseReasonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Причина расхода успешно создана!')
            return redirect('expenses:expense_reason_list')
    else:
        form = ExpenseReasonForm()

    return render(request, 'expenses/expense_reason_form.html', {
        'form': form,
        'title': 'Создать причину расхода'
    })


@login_required
@user_passes_test(is_admin_or_manager)
def expense_invoice_list(request):
    """Список накладных расхода"""
    invoices = ExpenseInvoice.objects.all().select_related('reason', 'created_by')
    return render(request, 'expenses/expense_invoice_list.html', {'invoices': invoices})


@login_required
@user_passes_test(is_admin_or_manager)
def expense_invoice_create(request):
    """Создание накладной расхода"""
    if request.method == 'POST':
        form = ExpenseInvoiceForm(request.POST)
        formset = ExpenseInvoiceItemFormSet(request.POST)

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

                messages.success(request, 'Накладная расхода успешно создана!')
                return redirect('expenses:expense_invoice_list')

            except Exception as e:
                messages.error(request, f'Ошибка при создании накладной: {str(e)}')
    else:
        last_invoice = ExpenseInvoice.objects.order_by('-id').first()
        next_number = f"РС-{(last_invoice.id + 1) if last_invoice else 1:06d}" if last_invoice else "РС-000001"

        form = ExpenseInvoiceForm(initial={'invoice_number': next_number})
        formset = ExpenseInvoiceItemFormSet()

    return render(request, 'expenses/expense_invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Создать накладную расхода'
    })


@login_required
@user_passes_test(is_admin_or_manager)
def expense_invoice_detail(request, pk):
    """Просмотр деталей накладной расхода"""
    invoice = get_object_or_404(ExpenseInvoice.objects.prefetch_related('expenseinvoiceitem_set__product'), pk=pk)
    items = invoice.expenseinvoiceitem_set.all()

    return render(request, 'expenses/expense_invoice_detail.html', {
        'invoice': invoice,
        'items': items
    })


@login_required
@user_passes_test(is_admin_or_manager)
def expense_invoice_complete(request, pk):
    """Завершение накладной расхода - уменьшение остатков"""
    invoice = get_object_or_404(ExpenseInvoice, pk=pk)

    if invoice.status != 'draft':
        messages.error(request, 'Накладная уже обработана или отменена!')
        return redirect('expenses:expense_invoice_detail', pk=pk)

    try:
        with transaction.atomic():
            for item in invoice.expenseinvoiceitem_set.all():
                if item.product.quantity < item.quantity:
                    messages.error(request, f'Недостаточно товара "{item.product.name}" на складе!')
                    return redirect('expenses:expense_invoice_detail', pk=pk)

            for item in invoice.expenseinvoiceitem_set.all():
                product = item.product
                product.quantity -= item.quantity
                product.save()

                StockTransaction.objects.create(
                    product=product,
                    transaction_type='out',
                    quantity=item.quantity,
                    user=request.user,
                    comment=f'Расход по накладной {invoice.invoice_number}. Причина: {invoice.reason.name}'
                )

            invoice.status = 'completed'
            invoice.save()

        messages.success(request, 'Накладная расхода успешно завершена! Остатки обновлены.')

    except Exception as e:
        messages.error(request, f'Ошибка при завершении накладной: {str(e)}')

    return redirect('expenses:expense_invoice_detail', pk=pk)


@login_required
@user_passes_test(is_admin_or_manager)
def expense_invoice_cancel(request, pk):
    """Отмена накладной расхода"""
    invoice = get_object_or_404(ExpenseInvoice, pk=pk)

    if invoice.status != 'draft':
        messages.error(request, 'Можно отменять только черновики!')
        return redirect('expenses:expense_invoice_detail', pk=pk)

    invoice.status = 'cancelled'
    invoice.save()

    messages.success(request, 'Накладная расхода отменена!')
    return redirect('expenses:expense_invoice_detail', pk=pk)

@login_required
@user_passes_test(is_admin_or_manager)
def expense_invoice_create_simple(request):
    """Упрощенное создание накладной расхода"""
    if request.method == 'POST':
        form = ExpenseInvoiceForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    invoice = form.save(commit=False)
                    invoice.created_by = request.user
                    invoice.save()

                    items_data = request.POST.get('items_data', '[]')
                    items = json.loads(items_data)

                    for item in items:
                        product = Product.objects.get(id=item['product_id'])
                        quantity = int(item['quantity'])

                        ExpenseInvoiceItem.objects.create(
                            invoice=invoice,
                            product=product,
                            quantity=quantity
                        )

                    invoice.update_total_amount()

                    messages.success(request, 'Накладная расхода успешно создана!')
                    return redirect('expenses:expense_invoice_list')

            except Exception as e:
                messages.error(request, f'Ошибка при создании накладной: {str(e)}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        last_invoice = ExpenseInvoice.objects.order_by('-id').first()
        next_number = f"РС-{(last_invoice.id + 1) if last_invoice else 1:06d}" if last_invoice else "РС-000001"
        form = ExpenseInvoiceForm(initial={'invoice_number': next_number})

    products_data = []
    for product in Product.objects.all():
        products_data.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': float(product.price),
            'quantity': product.quantity,
            'unit': product.unit
        })

    return render(request, 'expenses/expense_invoice_form_simple.html', {
        'form': form,
        'products': json.dumps(products_data),
        'title': 'Создать накладную расхода'
    })
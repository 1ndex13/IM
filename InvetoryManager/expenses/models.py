from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


class ExpenseReason(models.Model):
    """Причины расхода товара"""
    name = models.CharField(max_length=255, verbose_name='Название причины')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Причина расхода'
        verbose_name_plural = 'Причины расхода'

    def __str__(self):
        return self.name


class ExpenseInvoice(models.Model):
    """Накладная расхода товара"""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, verbose_name='Номер накладной')
    expense_date = models.DateField(verbose_name='Дата расхода')
    reason = models.ForeignKey(ExpenseReason, on_delete=models.PROTECT, verbose_name='Причина расхода')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Общая стоимость')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создал')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Накладная расхода'
        verbose_name_plural = 'Накладные расхода'
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"Накладная расхода {self.invoice_number} от {self.expense_date}"

    def update_total_amount(self):
        from django.db.models import Sum, F
        total = self.expenseinvoiceitem_set.aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )['total'] or 0
        self.total_amount = total
        self.save()


class ExpenseInvoiceItem(models.Model):
    """Строка накладной расхода"""
    invoice = models.ForeignKey(ExpenseInvoice, on_delete=models.CASCADE, verbose_name='Накладная')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='Общая стоимость')

    class Meta:
        verbose_name = 'Строка накладной расхода'
        verbose_name_plural = 'Строки накладной расхода'
        unique_together = ['invoice', 'product']

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.get_unit_display()}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.product.price
        super().save(*args, **kwargs)
        self.invoice.update_total_amount()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.update_total_amount()
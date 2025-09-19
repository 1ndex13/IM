from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Создал')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('in', 'Приход'),
        ('out', 'Расход'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, verbose_name='Тип операции')
    quantity = models.IntegerField(verbose_name='Количество')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата операции')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Операция с товаром'
        verbose_name_plural = 'Операции с товарами'
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.product.name} - {self.quantity}"
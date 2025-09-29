from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название категории')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ('шт', 'шт'),
        ('кг', 'Килограммы'),
        ('м', 'Метры'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название')
    sku = models.CharField(max_length=100, unique=True, verbose_name='Артикул (SKU)')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='шт', verbose_name='Единица измерения')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')
    min_stock = models.PositiveIntegerField(default=0, verbose_name='Минимальный запас')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Текущий остаток')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Фото')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Создал')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def is_low_stock(self):
        return self.quantity <= self.min_stock

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            max_size = (150, 150)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(self.image.path)

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


class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название поставщика')
    contact_person = models.CharField(max_length=255, blank=True, verbose_name='Контактное лицо')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    address = models.TextField(blank=True, verbose_name='Адрес')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['name']

    def __str__(self):
        return self.name


class PurchaseInvoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, verbose_name='Номер накладной')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='Поставщик')
    invoice_date = models.DateField(verbose_name='Дата накладной')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Общая сумма')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создал')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Накладная прихода'
        verbose_name_plural = 'Накладные прихода'
        ordering = ['-invoice_date', '-created_at']

    def __str__(self):
        return f"Накладная {self.invoice_number} от {self.invoice_date}"

    def update_total_amount(self):
        total = self.purchaseinvoiceitem_set.aggregate(
            total=models.Sum(models.F('quantity') * models.F('purchase_price'))
        )['total'] or 0
        self.total_amount = total
        self.save()


class PurchaseInvoiceItem(models.Model):
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, verbose_name='Накладная')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена закупки')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='Общая стоимость')

    class Meta:
        verbose_name = 'Строка накладной'
        verbose_name_plural = 'Строки накладной'
        unique_together = ['invoice', 'product']

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.get_unit_display()}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.purchase_price
        super().save(*args, **kwargs)

        self.invoice.update_total_amount()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.update_total_amount()
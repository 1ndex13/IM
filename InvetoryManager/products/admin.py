from django.contrib import admin
from .models import Product, StockTransaction, Category, Supplier, PurchaseInvoice, PurchaseInvoiceItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'quantity', 'min_stock', 'unit', 'created_at']
    list_filter = ['category', 'unit', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'date', 'user']
    list_filter = ['transaction_type', 'date']
    search_fields = ['product__name', 'user__email']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'created_at']
    search_fields = ['name', 'contact_person', 'phone']
    list_filter = ['created_at']

class PurchaseInvoiceItemInline(admin.TabularInline):
    model = PurchaseInvoiceItem
    extra = 1
    fields = ['product', 'quantity', 'purchase_price', 'total_price']
    readonly_fields = ['total_price']

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'invoice_date', 'status', 'total_amount', 'created_by']
    list_filter = ['status', 'invoice_date', 'supplier']
    search_fields = ['invoice_number', 'supplier__name']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [PurchaseInvoiceItemInline]
    fieldsets = (
        (None, {
            'fields': ('invoice_number', 'supplier', 'invoice_date', 'status')
        }),
        ('Финансы', {
            'fields': ('total_amount',)
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(PurchaseInvoiceItem)
class PurchaseInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'product', 'quantity', 'purchase_price', 'total_price']
    list_filter = ['invoice__supplier', 'invoice__invoice_date']
    search_fields = ['product__name', 'invoice__invoice_number']
from django.contrib import admin
from .models import ExpenseReason, ExpenseInvoice, ExpenseInvoiceItem


@admin.register(ExpenseReason)
class ExpenseReasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


class ExpenseInvoiceItemInline(admin.TabularInline):
    model = ExpenseInvoiceItem
    extra = 1
    fields = ['product', 'quantity', 'total_price']
    readonly_fields = ['total_price']


@admin.register(ExpenseInvoice)
class ExpenseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'expense_date', 'reason', 'status', 'total_amount', 'created_by']
    list_filter = ['status', 'expense_date', 'reason']
    search_fields = ['invoice_number', 'reason__name']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [ExpenseInvoiceItemInline]

    fieldsets = (
        (None, {
            'fields': ('invoice_number', 'expense_date', 'reason', 'status')
        }),
        ('Финансы', {
            'fields': ('total_amount',)
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(ExpenseInvoiceItem)
class ExpenseInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'product', 'quantity', 'total_price']
    list_filter = ['invoice__reason', 'invoice__expense_date']
    search_fields = ['product__name', 'invoice__invoice_number']
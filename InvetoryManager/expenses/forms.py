from django import forms
from .models import ExpenseInvoice, ExpenseInvoiceItem, ExpenseReason
from django.forms import inlineformset_factory


class ExpenseInvoiceForm(forms.ModelForm):
    class Meta:
        model = ExpenseInvoice
        fields = ['invoice_number', 'expense_date', 'reason', 'comment']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ExpenseInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = ExpenseInvoiceItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'product' in self.fields:
            self.fields['product'].widget.attrs.update({'class': 'form-control product-select'})
            products_with_prices = []
            for product in self.fields['product'].queryset:
                products_with_prices.append((
                    product.id,
                    product,
                    f"{product.name} - {product.price} ₸ (остаток: {product.quantity})"
                ))

            self.fields['product'].choices = [
                (product_id, display_text) for product_id, product, display_text in products_with_prices
            ]


ExpenseInvoiceItemFormSet = inlineformset_factory(
    ExpenseInvoice,
    ExpenseInvoiceItem,
    form=ExpenseInvoiceItemForm,
    extra=1,
    can_delete=True
)


class ExpenseReasonForm(forms.ModelForm):
    class Meta:
        model = ExpenseReason
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
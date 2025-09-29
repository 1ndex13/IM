from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('reasons/', views.expense_reason_list, name='expense_reason_list'),
    path('reasons/create/', views.expense_reason_create, name='expense_reason_create'),
    path('invoices/', views.expense_invoice_list, name='expense_invoice_list'),
    path('invoices/create/', views.expense_invoice_create, name='expense_invoice_create'),
    path('invoices/<int:pk>/', views.expense_invoice_detail, name='expense_invoice_detail'),
    path('invoices/<int:pk>/complete/', views.expense_invoice_complete, name='expense_invoice_complete'),
    path('invoices/<int:pk>/cancel/', views.expense_invoice_cancel, name='expense_invoice_cancel'),
]
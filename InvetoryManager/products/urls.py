from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('create/', views.product_create, name='create'),
    path('<int:pk>/update/', views.product_update, name='update'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
    path('transaction/', views.stock_transaction, name='transaction'),
    path('history/', views.transaction_history, name='history'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),

    path('purchase-invoices/', views.purchase_invoice_list, name='purchase_invoice_list'),
    path('purchase-invoices/create/', views.purchase_invoice_create, name='purchase_invoice_create'),
    path('purchase-invoices/<int:pk>/', views.purchase_invoice_detail, name='purchase_invoice_detail'),
    path('purchase-invoices/<int:pk>/complete/', views.purchase_invoice_complete, name='purchase_invoice_complete'),
    path('purchase-invoices/<int:pk>/cancel/', views.purchase_invoice_cancel, name='purchase_invoice_cancel'),
]
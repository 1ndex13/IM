from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('stock/', views.stock_report, name='stock_report'),
    path('movement/', views.movement_report, name='movement_report'),
    path('turnover/', views.turnover_report, name='turnover_report'),
]
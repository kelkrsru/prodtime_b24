from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.index, name='index'),
    path('for-report-stock', views.report_stock, name='report_stock'),
]

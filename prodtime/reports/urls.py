from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('report-deals/', views.report_deals, name='report_deals'),
    path('report-production/', views.report_production, name='report_production'),
]

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('report-deals/', views.report_deals, name='report_deals'),
]

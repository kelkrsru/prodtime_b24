from django.urls import path
from . import views

app_name = 'dealcard'

urlpatterns = [
    path('', views.index, name='index'),
    path('save/', views.save, name='save'),
    path('create/', views.create, name='create'),
    path('create-doc/', views.create_doc, name='create-doc'),
    path('copy-products/', views.copy_products, name='copy-products'),
    path('write-factory-number/', views.write_factory_number,
         name='write-factory-number'),
    path('update-factory-number/', views.update_factory_number,
         name='update-factory-number'),
    path('send-equivalent/', views.send_equivalent, name='send-equivalent'),
    path('export-excel/', views.export_excel, name='export-excel'),
]

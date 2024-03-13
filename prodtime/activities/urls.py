from django.urls import path

from . import views

app_name = 'activities'

urlpatterns = [
    path('install/', views.install, name='install'),
    path('uninstall/', views.uninstall, name='uninstall'),
    path('send_to_db/', views.send_to_db, name='send_to_db'),
    path('get_from_db/', views.get_from_db, name='get_from_db'),
    path('update-finish/', views.update_finish, name='update-finish'),
    path('update-income/', views.update_income, name='update-income'),
]

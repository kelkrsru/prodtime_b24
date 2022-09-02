from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('settings.urls', namespace='settings')),
    path('install/', include('core.urls', namespace='core')),
    path('dealcard/', include('dealcard.urls', namespace='dealcard')),
    path('quotecard/', include('quotecard.urls', namespace='quotecard')),
    path('admin/', admin.site.urls),
]

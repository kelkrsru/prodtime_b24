from django.contrib import admin
from .models import SettingsPortal


class SettingsPortalAdmin(admin.ModelAdmin):
    list_display = (
        'portal',
    )


admin.site.register(SettingsPortal, SettingsPortalAdmin)

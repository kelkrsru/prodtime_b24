from django.contrib import admin
from .models import SettingsPortal, Numeric, AssociativeYearNumber


class SettingsPortalAdmin(admin.ModelAdmin):
    list_display = (
        'portal',
    )


@admin.register(Numeric)
class NumericAdmin(admin.ModelAdmin):
    list_display = ('portal', 'year', 'last_number')
    list_editable = ('year', 'last_number')
    list_filter = ('portal',)


@admin.register(AssociativeYearNumber)
class AssociativeYearNumberAdmin(admin.ModelAdmin):
    list_display = ('portal', 'year', 'year_code')
    list_editable = ('year', 'year_code')
    list_filter = ('portal',)


admin.site.register(SettingsPortal, SettingsPortalAdmin)

from django.contrib import admin
import settings.models as settings_models


@admin.register(settings_models.SettingsPortal)
class SettingsPortalAdmin(admin.ModelAdmin):
    list_display = ('portal',)


@admin.register(settings_models.Numeric)
class NumericAdmin(admin.ModelAdmin):
    list_display = ('portal', 'year', 'last_number')
    list_editable = ('year', 'last_number')
    list_filter = ('portal',)


@admin.register(settings_models.AssociativeYearNumber)
class AssociativeYearNumberAdmin(admin.ModelAdmin):
    list_display = ('portal', 'year', 'year_code')
    list_editable = ('year', 'year_code')
    list_filter = ('portal',)


@admin.register(settings_models.SettingsForReportStock)
class SettingsForReportStockAdmin(admin.ModelAdmin):
    list_display = ('portal',)

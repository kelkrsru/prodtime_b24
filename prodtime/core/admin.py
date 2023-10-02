from django.contrib import admin
from .models import Portals, TemplateDocFields, Responsible


class PortalsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'member_id',
        'name',
        'auth_id_create_date',
    )


class TemplateDocFieldsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'code',
        'code_b24',
        'code_db',
    )


@admin.register(Responsible)
class ResponsibleAdmin(admin.ModelAdmin):
    list_display = ('id_b24', 'first_name', 'last_name')


admin.site.register(Portals, PortalsAdmin)
admin.site.register(TemplateDocFields, TemplateDocFieldsAdmin)

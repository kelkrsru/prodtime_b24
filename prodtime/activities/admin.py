from django.contrib import admin

from .models import Activity, FieldsActivity, OptionsForSelect


@admin.register(OptionsForSelect)
class OptionsForSelectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'fields')
    list_filter = ('fields',)


admin.site.register(Activity)
admin.site.register(FieldsActivity)

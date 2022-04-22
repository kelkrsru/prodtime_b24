from django.contrib import admin
from .models import ProdTime


class ProdTimeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'product_id_b24',
        'deal_id',
        'portal',
    )


admin.site.register(ProdTime, ProdTimeAdmin)

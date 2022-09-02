from django.contrib import admin
from .models import ProdTimeDeal


class ProdTimeDealAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'product_id_b24',
        'deal_id',
        'portal',
    )


admin.site.register(ProdTimeDeal, ProdTimeDealAdmin)

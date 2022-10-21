from django.contrib import admin
from dealcard.models import Deal, ProdTimeDeal


class ProdTimeDealAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'product_id_b24',
        'deal_id',
        'portal',
    )


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'general_number', 'last_factory_number',
                    'portal')


admin.site.register(ProdTimeDeal, ProdTimeDealAdmin)

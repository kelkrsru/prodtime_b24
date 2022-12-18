from django.contrib import admin
from dealcard.models import Deal, ProdTimeDeal


class ProdTimeDealAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'product_id_b24',
        'sort',
        'factory_number',
        'deal_id',
        'portal',
    )
    search_fields = ('deal_id',)
    list_editable = ('sort',)


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'general_number', 'last_factory_number',
                    'portal')


admin.site.register(ProdTimeDeal, ProdTimeDealAdmin)

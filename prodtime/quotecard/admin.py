from django.contrib import admin
from .models import ProdTimeQuote


@admin.register(ProdTimeQuote)
class ProdTimeQuoteAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'product_id_b24',
        'quote_id',
        'portal',
    )
    search_fields = ['quote_id', ]

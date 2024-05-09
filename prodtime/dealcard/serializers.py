from rest_framework import serializers

from core.bitrix24.bitrix24 import ProductInCatalogB24, create_portal, ProductRowB24
from dealcard.models import ProdTimeDeal


class ProdTimeDealSerializer(serializers.ModelSerializer):
    product_id_in_catalog_b24 = serializers.SerializerMethodField()

    def get_product_id_in_catalog_b24(self, obj):
        get_catalog_id = True if self.context.get('request').query_params.get('get_catalog_id') else False
        if get_catalog_id:
            portal = create_portal('895413ed6c89998e579c7d38f4faa520')
            product_row = ProductRowB24(portal, obj.product_id_b24)
            product_in_catalog = ProductInCatalogB24(portal, product_row.id_in_catalog)
            return str(product_in_catalog.id)
        return False

    class Meta:
        model = ProdTimeDeal
        fields = '__all__'  # , 'created', 'updated', 'product_id_in_catalog_b24')

from django.shortcuts import get_object_or_404, render

from core.bitrix24.bitrix24 import ListEntitiesB24, BatchB24
from core.models import Portals
from settings.models import SettingsPortal, SettingsForReportStock


class ReportProdtime:
    """Общий класс отчетов для программы Сроки производства."""

    def __init__(self, portal: Portals):
        self.portal = portal
        self.settings_portal = self._get_settings_portal()

    def _get_settings_portal(self):
        return get_object_or_404(SettingsPortal, portal=self.portal)


class ReportStock(ReportProdtime):
    """Класс отчета по остаткам."""

    def __init__(self, portal: Portals):
        super().__init__(portal)
        self.settings_for_report_stock = self._get_settings_for_report_stock()
        self.min_stock_code = self.settings_for_report_stock.min_stock_code
        self.stock_id = self.settings_for_report_stock.stock_id
        self.all_remains_for_stock = self._get_all_remains_for_stock()
        self.products_in_catalog = self._get_products_in_catalog().results
        self.remains_products = self._get_all_remains_products()

    def _get_settings_for_report_stock(self):
        return get_object_or_404(SettingsForReportStock, portal=self.portal)

    def _get_all_remains_for_stock(self):
        """Получить все остатки по складу."""
        def _create_finish_dict(remains):
            finish_dict = dict()
            for entity in remains:
                entity['amount'] = 0 if not entity.get('amount') else entity.get('amount')
                entity['quantityReserved'] = 0 if not entity.get('quantityReserved') else entity.get('quantityReserved')
                entity['quantityAvailable'] = entity.get('amount') - entity.get('quantityReserved')
                finish_dict[entity.get('productId')] = entity
            return finish_dict

        all_remains = ListEntitiesB24(self.portal, {'storeId': self.stock_id}, 'store').entities
        return _create_finish_dict(all_remains)

    def _get_products_in_catalog(self):
        """Получить товары из каталога Б24, которые участвуют в остатках."""
        queries = {f'prod{i}': {'method': 'catalog.product.get', 'params': {'id': prod}} for i, prod in
                   enumerate(self.all_remains_for_stock)}
        return BatchB24(self.portal, queries)

    def _get_all_remains_products(self):
        """Сформировать остатки с товарами."""
        remains_products = dict(self.all_remains_for_stock)
        for product_in_catalog in self.products_in_catalog:
            product_in_catalog = product_in_catalog.get('product')
            product_in_catalog_id = product_in_catalog.get('id')
            remain_product = remains_products.get(product_in_catalog_id)
            remain_product['no_available'] = "-"
            remain_product['color'] = False

            if product_in_catalog.get(self.settings_for_report_stock.task_id_code):
                remain_product['task_id'] = product_in_catalog.get(self.settings_for_report_stock.task_id_code).get('value')
            if product_in_catalog.get(self.settings_for_report_stock.task_responsible_code):
                remain_product['task_responsible'] = product_in_catalog.get(self.settings_for_report_stock.task_responsible_code).get('value')

            remain_product['name'] = product_in_catalog.get('name')
            if product_in_catalog.get(self.min_stock_code):
                remain_product['min_stock'] = int(product_in_catalog.get(self.min_stock_code).get('value'))
                no_available = remain_product.get('min_stock') - remain_product.get('quantityAvailable')
                if no_available >= 0:
                    remain_product['no_available'] = no_available
                    remain_product['color'] = True
            else:
                remains_products[product_in_catalog.get('id')]['min_stock'] = 'Не указан'
        return remains_products.values()
from django.shortcuts import get_object_or_404

from core.bitrix24.bitrix24 import ListEntitiesB24, BatchB24
from settings.models import SettingsPortal, SettingsForReportStock


class ReportProdtime:
    """Общий класс отчетов для программы Сроки производства."""

    def __init__(self, portal, params):
        self.portal = portal
        self.settings_portal = self._get_settings_portal()
        self.params = params

    def _get_settings_portal(self):
        return get_object_or_404(SettingsPortal, portal=self.portal)


class ReportStock(ReportProdtime):
    """Класс отчета по остаткам."""

    def __init__(self, portal, params):
        super().__init__(portal, params)
        self.settings_for_report_stock = self._get_settings_for_report_stock()
        self.min_stock_code = self.settings_for_report_stock.min_stock_code
        self.max_stock_code = self.settings_for_report_stock.max_stock_code
        self.stock_id = self.settings_for_report_stock.stock_id
        self.all_remains_for_stock = self._get_all_remains_for_stock()
        self.products_in_catalog = self._get_products_in_catalog().results
        self.show_article = self._get_params('show_article')
        self.show_null_min_max_stock = self._get_params('show_null_min_max_stock')
        self.remains_products = self._get_all_remains_products()

    def _get_settings_for_report_stock(self):
        return get_object_or_404(SettingsForReportStock, portal=self.portal)

    def _get_params(self, param_name):
        if not self.params or param_name not in self.params:
            return None
        return self.params.get(param_name)

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
            remain_product['flag_task'] = False
            remain_product['flag_task_average'] = False
            remain_product['color'] = False

            # Проверка на параметры
            if (self.show_article == 'Y' and
                    (not product_in_catalog.get(self.settings_portal.is_auto_article_code) or
                     product_in_catalog.get(self.settings_portal.is_auto_article_code).get('valueEnum') == 'Нет')):
                remains_products.pop(remain_product.get('productId'))
                continue
            if (self.show_article == 'N' and
                    (not product_in_catalog.get(self.settings_portal.is_auto_article_code) or
                     product_in_catalog.get(self.settings_portal.is_auto_article_code).get('valueEnum') == 'Да')):
                remains_products.pop(remain_product.get('productId'))
                continue

            if (self.show_null_min_max_stock == 'N' and not product_in_catalog.get(self.max_stock_code)
                    and not product_in_catalog.get(self.min_stock_code)):
                remains_products.pop(remain_product.get('productId'))
                continue

            # Проверяем есть ли задача на минимальный остаток
            if product_in_catalog.get(self.settings_for_report_stock.task_id_code):
                remain_product['task_id'] = product_in_catalog.get(
                    self.settings_for_report_stock.task_id_code).get('value')
            if product_in_catalog.get(self.settings_for_report_stock.task_responsible_code):
                remain_product['task_responsible'] = product_in_catalog.get(
                    self.settings_for_report_stock.task_responsible_code).get('value')
            # Проверяем есть ли задача на средний остаток
            if product_in_catalog.get(self.settings_for_report_stock.task_average_id_code):
                remain_product['task_average_id'] = product_in_catalog.get(
                    self.settings_for_report_stock.task_average_id_code).get('value')
            if product_in_catalog.get(self.settings_for_report_stock.task_average_responsible_code):
                remain_product['task_average_responsible'] = product_in_catalog.get(
                    self.settings_for_report_stock.task_average_responsible_code).get('value')

            remain_product['name'] = product_in_catalog.get('name')
            # Проверка на минимальный остаток
            if product_in_catalog.get(self.min_stock_code):
                remain_product['min_stock'] = int(product_in_catalog.get(self.min_stock_code).get('value'))
                no_available = remain_product.get('min_stock') - remain_product.get('quantityAvailable')
                if no_available >= 0:
                    remain_product['no_available'] = f'-{no_available}'
                    remain_product['flag_task'] = True
                    remain_product['color'] = True
            else:
                remains_products[product_in_catalog.get('id')]['min_stock'] = 'Не указан'
            # Проверка на максимальный остаток
            if product_in_catalog.get(self.max_stock_code):
                remain_product['max_stock'] = int(product_in_catalog.get(self.max_stock_code).get('value'))
                no_available = remain_product.get('quantityAvailable') - remain_product.get('max_stock')
                if no_available >= 0:
                    remain_product['no_available'] = f'+{no_available}'
                    remain_product['flag_task'] = False
                    remain_product['color_max'] = True
            else:
                remains_products[product_in_catalog.get('id')]['max_stock'] = 'Не указан'
            # Проверка на средний остаток
            if type(remain_product.get('min_stock')) == int and type(remain_product.get('max_stock')) == int:
                average_value = (remain_product.get('min_stock') + remain_product.get('max_stock')) / 2
                if average_value > remain_product.get('quantityAvailable') > remain_product.get('min_stock'):
                    remain_product['no_available'] = f''
                    remain_product['flag_task_average'] = True
                    remain_product['color_average'] = True
        return remains_products.values()

from django.shortcuts import get_object_or_404

from core.bitrix24.bitrix24 import ListEntitiesB24, BatchB24, ListProductRowsB24
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
        self.considered_paid_stages = self.settings_for_report_stock.considered_paid_stages
        self.all_remains_for_stock = self._get_all_remains_for_stock()
        self.products_in_catalog = self._get_products_in_catalog().results
        self.show_article = self._get_params('show_article')
        self.show_null_min_max_stock = self._get_params('show_null_min_max_stock')
        self.remains_products = self._get_all_remains_products()

    @staticmethod
    def _safe_int(value, default = None):
        """Безопасное преобразование в int."""
        if value is None or value == '':
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def _get_settings_for_report_stock(self):
        return get_object_or_404(SettingsForReportStock, portal=self.portal)

    def _get_params(self, param_name):
        return self.params.get(param_name) if self.params else None

    def _get_all_remains_for_stock(self):
        """Получить все остатки по складу и привести к словарю {productId: data}."""

        def normalize_remain(entity):
            amount = self._safe_int(entity.get('amount'), 0)
            reserved = self._safe_int(entity.get('quantityReserved'), 0)
            return {
                'productId': entity.get('productId'),
                'amount': amount,
                'quantityReserved': reserved,
                'quantityAvailable': amount - reserved,
            }

        entities = ListEntitiesB24(self.portal, {'storeId': self.stock_id}, 'store').entities
        return {ent['productId']: normalize_remain(ent) for ent in entities}

    def _get_paid_considered_all_productrows(self):
        """Получить все товарные позиции в сделках, которые находятся в стадиях, где товар считается оплаченным."""
        def _get_paid_considered_deal_ids():
            """Получить все ids сделок, которые находятся в стадиях, где товар считается оплаченным."""
            if not self.considered_paid_stages:
                return None
            filter_entities = {'@STAGE_ID': self.considered_paid_stages}
            return ListEntitiesB24(self.portal, filter_entities, 'deal').entities

        def extract_entities_ids(entities_b24, as_int=True):
            """
            Извлекает список ID из массива сделок.

            :param entities_b24: список словарей (сделки из Bitrix)
            :param as_int: True -> вернет список int, False -> список строк
            :return: список ID
            """
            ids = []
            for deal in entities_b24:
                deal_id = deal.get("ID")
                if deal_id:  # проверяем, что ID есть и не пустой
                    ids.append(int(deal_id) if as_int else str(deal_id))
            return ids

        deals = _get_paid_considered_deal_ids()
        if not deals:
            return None
        deal_ids = extract_entities_ids(deals, as_int=True)
        filter_productrows = {'=ownerType': 'D', '=ownerID': deal_ids}
        productrows = ListProductRowsB24(self.portal, filter_productrows).entities

        return productrows

    def _get_paid_totals_by_product(self):
        """
        Считает сумму оплаченного количества по каждому productId.
        :return: dict {productId: total_quantity}
        """
        paid_rows = self._get_paid_considered_all_productrows() or []
        totals = {}

        for row in paid_rows:
            pid = row.get("productId")
            qty = self._safe_int(row.get("quantity"), 0)
            totals[pid] = totals.get(pid, 0) + qty

        return totals

    def _get_products_in_catalog(self):
        """Получить все продукты каталога Б24, которые есть в остатках на складах."""
        product_ids = self.all_remains_for_stock.keys()
        queries = {
            f'prod{i}': {'method': 'catalog.product.get', 'params': {'id': prod_id}}
            for i, prod_id in enumerate(product_ids)
        }
        return BatchB24(self.portal, queries)

    def _filter_product(self, product):
        """Проверка условий фильтрации товара."""
        article_field = product.get(self.settings_portal.is_auto_article_code)
        has_article = article_field and article_field.get('valueEnum') in ('Да', 'Y')
        no_has_article = article_field and article_field.get('valueEnum') in ('Нет', 'N')

        if self.show_article == 'Y' and not has_article:
            return False
        if self.show_article == 'N' and not no_has_article:
            return False

        if (self.show_null_min_max_stock == 'N'
                and not product.get(self.max_stock_code)
                and not product.get(self.min_stock_code)):
            return False
        return True

    def _fill_task_fields(self, remain_product, product):
        """Заполнение информации о задачах."""
        s = self.settings_for_report_stock
        task_fields = {
            'task_id': s.task_id_code,
            'task_responsible': s.task_responsible_code,
            'task_average_id': s.task_average_id_code,
            'task_average_responsible': s.task_average_responsible_code,
        }
        for key, field_code in task_fields.items():
            if product.get(field_code):
                remain_product[key] = product[field_code].get('value')

    def _check_min_stock(self, remain_product, product):
        if product.get(self.min_stock_code):
            min_stock = self._safe_int(product[self.min_stock_code].get('value'))
            remain_product['min_stock'] = min_stock
            no_available = min_stock - remain_product['quantityAvailable']
            if no_available >= 0:
                remain_product.update({
                    'no_available': f'-{no_available}',
                    'flag_task': True,
                    'color': True
                })
        else:
            remain_product['min_stock'] = 'Не указан'

    def _check_max_stock(self, remain_product, product):
        if product.get(self.max_stock_code):
            max_stock = self._safe_int(product[self.max_stock_code].get('value'))
            remain_product['max_stock'] = max_stock
            no_available = remain_product['quantityAvailable'] - max_stock
            if no_available >= 0:
                remain_product.update({
                    'no_available': f'+{no_available}',
                    'flag_task': False,
                    'color_max': True
                })
        else:
            remain_product['max_stock'] = 'Не указан'

    @staticmethod
    def _check_average_stock(remain_product):
        if isinstance(remain_product.get('min_stock'), int) and isinstance(remain_product.get('max_stock'), int):
            avg_value = (remain_product['min_stock'] + remain_product['max_stock']) / 2
            if remain_product['min_stock'] < remain_product['quantityAvailable'] < avg_value:
                remain_product.update({
                    'no_available': '',
                    'flag_task_average': True,
                    'color_average': True
                })

    def _get_all_remains_products(self):
        """Формирование отчета по остаткам с привязкой к товарам."""
        remains_products = dict(self.all_remains_for_stock)

        # заранее считаем оплаченные количества
        paid_totals = self._get_paid_totals_by_product()

        for prod_data in self.products_in_catalog:
            product = prod_data.get('product')
            pid = product.get('id')
            paid = paid_totals.get(pid, 0)

            remain_product = remains_products.get(pid)
            if not remain_product:
                continue

            remain_product.update({
                'no_available': '-',
                'flag_task': False,
                'flag_task_average': False,
                'color': False,
                'paid': paid,
            })

            # уменьшаем доступное количество с учетом оплаченного
            remain_product['quantityReserved'] = remain_product['quantityReserved'] - paid

            if not self._filter_product(product):
                remains_products.pop(pid, None)
                continue
            remain_product['name'] = product.get('name')
            self._fill_task_fields(remain_product, product)
            self._check_min_stock(remain_product, product)
            self._check_max_stock(remain_product, product)
            self._check_average_stock(remain_product)

        return remains_products.values()

import copy

from django.db import transaction

from core.bitrix24.bitrix24 import ProductRowB24, ProductInCatalogB24, BatchB24, DealB24, SmartProcessB24
from decimal import Decimal

from core.management.commands.checkstoreproducts import logger
from core.models import ProdTime
from dealcard.models import ProdTimeDeal


class ProductRow:
    """Класс-обертка над строкой товара в CRM."""
    def __init__(self, portal, product_row_id: int):
        self.portal = portal
        self.id = product_row_id
        self._api = ProductRowB24(portal, product_row_id)

    def delete(self):
        self._api.delete()

    def add_to_owner(self, owner_id: int, owner_type: str, product_catalog_id: int, price: Decimal, product_name: str = None,  quantity: int = 1, discount_type_id: int = 2,
                     discount_rate: Decimal = 0, discount_sum: Decimal = 0, tax_rate: Decimal = 0, tax_included: bool = False, measure_code: int = None, sort: int = 10):
        fields = {
            'ownerId': owner_id,
            'ownerType': owner_type,
            'productId': product_catalog_id,
            'productName': product_name,
            'price': price,
            'quantity': quantity,
            'discountTypeId': discount_type_id,
            'discountRate': discount_rate,
            'discountSum': discount_sum,
            'taxRate': tax_rate,
            'taxIncluded': 'Y' if tax_included else 'N',
            'measureCode': measure_code,
            'sort': sort
        }
        return self._api.add(fields)

    @property
    def catalog_id(self):
        return self._api.id_in_catalog

    @property
    def properties(self):
        return self._api.properties

class CatalogProduct:
    """Класс-обертка над товаром каталога в CRM."""
    def __init__(self, portal, product_id: int):
        self.portal = portal
        self.id = product_id
        self._api = ProductInCatalogB24(portal, product_id)

    @property
    def properties(self) -> dict:
        return self._api.properties

    def has_factory_number_enabled(self, factory_number_code: str):
        prop = self.properties.get(factory_number_code)
        return prop is not None and prop.get('valueEnum') != 'Нет'


class ProductSplitter:
    """Класс разделения продуктов на количество 1, если начальное количество больше 1."""
    def __init__(self, portal, deal_id: str, settings_portal, logger):
        self.portal = portal
        self.deal_id = deal_id
        self.settings_portal = settings_portal
        self.products_to_split = []
        # self.catalog_cache = {}  # кэш по product_id_b24

    def split_all(self):
        """Основной метод: собрать товары, сформировать batch, выполнить, сохранить в БД."""
        logger.info(f'Запущен основной метод split_all')
        self._collect_products_to_split()
        if not self.products_to_split:
            logger.info(f'Нет товаров, которые необходимо разделить.')
            return

        logger.info(f'{self.products_to_split=}')
        with transaction.atomic():
            self._create_new_products_in_db()
            self._update_product_sort()

        products_properties = self._build_products_to_create()
        result = self._create_products_in_b24(products_properties)
        logger.info(f'{result=}')
        self._update_products_ids_b24()


    def _collect_products_to_split(self):
        """Собираем товары, которые нужно разбить."""
        logger.info(f'Запущен метод _collect_products_to_split')
        products_in_db = ProdTimeDeal.objects.filter(portal=self.portal, deal_id=self.deal_id).order_by('sort')
        logger.info(f'{products_in_db=}')

        for product_in_db in products_in_db:
            logger.info(f'{product_in_db=}')
            if not product_in_db.catalog_product_id_b24:
                logger.info(f'Товарная позиция {product_in_db} не является товаром каталога. Пропускаем.')
                continue
            catalog_product_id = product_in_db.catalog_product_id_b24
            logger.info(f'{catalog_product_id=}')
            catalog_product = CatalogProduct(self.portal, catalog_product_id)
            logger.info(f'{catalog_product.properties=}')
            if not self._should_split(product_in_db, catalog_product):
                continue
            self.products_to_split.append(product_in_db)
            # self.catalog_cache[catalog_product_id] = catalog_product
        logger.info(f'{self.products_to_split=}')
        # logger.info(f'{self.catalog_cache=}')

    @staticmethod
    def is_valid_quantity(product):
        """Проверяет, что количество больше 1 и является целым числом."""
        return product.quantity > 1 and float(product.quantity).is_integer()

    def _should_split(self, product, catalog_product):
        """Проверяет нужно ли разделить товар."""
        if not self.is_valid_quantity(product): # Количество товара не валидно
            logger.info(f'Количество товара {product} равно {product.quantity} - является не валидным для разделения.')
            return False
        if not FactoryNumberAssigner.should_create_factory_number(product, catalog_product, self.settings_portal):
            return False
        return  True

    # def _get_catalog_product(self, catalog_product_id: int):
    #     if catalog_product_id not in self.catalog_cache:
    #         self.catalog_cache[catalog_product_id] = CatalogProduct(self.portal, catalog_product_id)
    #     return self.catalog_cache[catalog_product_id]

    def _create_new_products_in_db(self):
        """Создаёт новые ProdTimeDeal в БД приложения на основе self.products_to_split."""
        neg_id_counter = -1
        for product_in_db in self.products_to_split:
            logger.info(f'Обрабатываем товар {product_in_db.id=} {product_in_db}')
            qty = int(product_in_db.quantity) # Проверка на int уже выполнена в методе is_valid_quantity
            logger.info(f'Начальное количество товара = {qty}')
            for i in range(qty):
                logger.info(f'Шаг цикла = {i}')
                new_product_in_db = copy.deepcopy(product_in_db)
                new_product_in_db.id = None
                new_product_in_db.quantity = 1
                new_product_in_db.bonus_sum = product_in_db.bonus_sum / qty
                new_product_in_db.tax_sum = product_in_db.tax_sum / qty
                new_product_in_db.sum = product_in_db.sum / qty
                new_product_in_db.product_id_b24 = neg_id_counter
                neg_id_counter -= 1

                new_product_in_db.save()
            product_in_db.delete()

    def _update_product_sort(self):
        """Метод, который установит правильную сортировку для товаров в БД приложения."""
        products_in_db = ProdTimeDeal.objects.filter(portal=self.portal, deal_id=self.deal_id).only('id', 'sort').order_by('sort')
        for i, product_in_db in enumerate(products_in_db, start=10):
            product_in_db.sort = i
        ProdTimeDeal.objects.bulk_update(products_in_db, ['sort'])


    def _build_products_to_create(self):
        """Генерирует массив с товарами для их создания в сделке Битрикс24."""
        logger.info(f'Собираем массив свойств товаров для передачи их в сделку.')
        rows = []
        products_in_db = ProdTimeDeal.objects.filter(portal=self.portal, deal_id=self.deal_id).only('id', 'sort', 'catalog_product_id_b24', 'price', 'quantity',
                                                                                                    'bonus_type_id', 'bonus', 'bonus_sum', 'tax', 'measure_code',
                                                                                                    'measure_name').order_by('sort')
        for product_in_db in products_in_db:
            logger.info(f'Свойства для товара {product_in_db.id=} {product_in_db}.')
            fields = {
                'PRODUCT_ID': product_in_db.catalog_product_id_b24,
                'PRICE': str(product_in_db.price),
                'QUANTITY': str(product_in_db.quantity),
                'DISCOUNT_TYPE_ID': product_in_db.bonus_type_id,
                'DISCOUNT_RATE': str(product_in_db.bonus),
                'DISCOUNT_SUM': str(product_in_db.bonus_sum),
                'TAX_RATE': str(product_in_db.tax),
                'TAX_INCLUDED': 'Y' if product_in_db.tax_included else 'N',
                'MEASURE_NAME': product_in_db.measure_name,
                'SORT': product_in_db.sort,
            }
            rows.append(fields)
        logger.info(f'{rows=}')
        return rows

    def _create_products_in_b24(self, rows):
        """Устанавливает товары в Битрикс24 на основе созданного массива."""
        deal_b24 = DealB24(self.portal, int(self.deal_id))
        return deal_b24.set_products(rows)

    def _update_products_ids_b24(self):
        """Обновляет ID товарных позиций в БД приложения, после их создания в сделке."""
        deal_b24 = DealB24(self.portal, int(self.deal_id))
        deal_b24.get_all_products()
        for product_in_deal in deal_b24.products:
            sort = product_in_deal.get('SORT')
            products_in_db = ProdTimeDeal.objects.get(portal=self.portal, deal_id=self.deal_id, sort=sort)
            products_in_db.product_id_b24 = product_in_deal.get('ID')
            products_in_db.save()


class FactoryNumberCreator:
    """Класс, который создает заводские номера для товаров."""
    def __init__(self, deal, settings_portal):
        self.deal = deal
        self.settings_portal = settings_portal
        self.active_factory_number = None

    def create_factory_numbers(self):
        """Основной метод, который создает заводские номера."""
        factory_number = f"{self.deal.general_number}{self.deal.last_factory_number + 1}"
        self.active_factory_number = factory_number

    def last_factory_number_add(self):
        """Метод, который увеличивает последний заводской номер на 1."""
        try:
            self.deal.last_factory_number += 1
            self.deal.save(update_fields=['last_factory_number'])
        except Exception as ex:
            raise RuntimeError('Ошибка при увеличении последнего заводского номера в сделке.') from ex

    def build_smart_element_to_create(self, deal_b24):
        """Генерирует член массива элементов смарт процесса для их создания в смарт процессе Заводские номера в Битрикс24."""
        return {
            'title': self.active_factory_number,
            'assigned_by_id': deal_b24.responsible,
            'parentId2': self.deal.deal_id,
            'company_id': deal_b24.company_id,
            self.settings_portal.smart_factory_number_code: self.active_factory_number
        }

    def build_product_row_add_smart_element(self, product):
        """Генерирует член массива товаров для их добавления в элемент смарт процесса Заводские номера в Битрикс24."""
        return {
                'ownerId': product.smart_id_factory_number,
                'ownerType': self.settings_portal.smart_factory_number_short_code,
                'productId': product.catalog_product_id_b24,
                'quantity': 1,
            }


class FactoryNumberAssigner:
    """Основной класс, который реализует бизнес-логику присвоения заводских номеров."""
    def __init__(self, portal, settings_portal, deal, deal_b24):
        self.portal = portal
        self.settings_portal = settings_portal
        self.deal = deal
        self.deal_b24 = deal_b24

    @staticmethod
    def should_create_factory_number(product, catalog_product, settings_portal):
        """Проверяет нужно ли товару присваивать заводской номер."""
        if not catalog_product.has_factory_number_enabled(settings_portal.factory_number_code):  # Для товара каталога не нужно присваивать заводские номера
            logger.info(f'Для товара {product} не нужно присваивать заводской номер, признак не установлен.')
            return False
        if product.factory_number and product.smart_id_factory_number:  # Не присваивать если оба поля factory_number и smart_id_factory_number заполнены уже
            logger.info(f'У товара {product} уже заполнены оба поля {product.factory_number=} и {product.smart_id_factory_number=}')
            return False
        return True

    def execute(self) -> dict:
        try:
            self._split_products_if_needed()
            result = self._assign_numbers()
            return self._make_success_response(result)
        except Exception as e:
            return {'result': 'error', 'info': str(e)}

    def _split_products_if_needed(self):
        splitter = ProductSplitter(self.portal, self.deal.deal_id, self.settings_portal, logger)
        splitter.split_all()

    def _assign_numbers(self):
        products_in_db = ProdTimeDeal.objects.filter(portal=self.portal, deal_id=self.deal.deal_id).order_by('sort')
        result_work = ''
        creator = FactoryNumberCreator(self.deal, self.settings_portal)
        queries_for_smart_elements = dict()
        queries_for_products_to_smart_elements = dict()
        smart_process_b24 = SmartProcessB24(self.portal, self.settings_portal.smart_factory_number_id)

        for product_in_db in products_in_db:
            catalog_product = CatalogProduct(self.portal, product_in_db.catalog_product_id_b24)
            if not self.should_create_factory_number(product_in_db, catalog_product, self.settings_portal):
                continue
            try:
                creator.create_factory_numbers()
                product_in_db.factory_number = creator.active_factory_number
                product_in_db.save(update_fields=['factory_number'])
            except Exception as ex:
                raise RuntimeError(f'Ошибка при назначении заводского номера товару c ID = {product_in_db.product_id_b24} Name = {product_in_db.name} в БД приложения.') from ex
            creator.last_factory_number_add()

            fields = creator.build_smart_element_to_create(self.deal_b24)
            queries_for_smart_elements[f"add_{product_in_db.product_id_b24}"] = {"method": "crm.item.add", "params":
                {"entityTypeId": int(smart_process_b24.properties.get('type').get('entityTypeId')),"fields": fields}}
            result_work += f"\nДля товара {product_in_db.name} установлен заводской номер {product_in_db.factory_number}"

        logger.info(f'Созданный словарь запросов: {queries_for_smart_elements=}')
        result = BatchB24(self.portal, queries_for_smart_elements).results
        logger.info(f'{result=}')
        ### Вот здесь нужна проверка на ошибки result

        mapping = {
            item['item'][self.settings_portal.smart_factory_number_code]: item['item']['id']
            for item in result
            if item['item'][self.settings_portal.smart_factory_number_code]
        }

        # Загружаем все нужные записи одним запросом
        products_in_db_for_update = list(ProdTimeDeal.objects.filter(
            portal=self.portal,
            deal_id=self.deal.deal_id,
            factory_number__in=mapping.keys()
        ))

        # Обновляем нужное поле у каждого объекта
        for product_in_db_for_update in products_in_db_for_update:
            product_in_db_for_update.smart_id_factory_number = mapping[product_in_db_for_update.factory_number]

        # Массовое обновление одним запросом
        ProdTimeDeal.objects.bulk_update(products_in_db_for_update, ['smart_id_factory_number'])

        products_in_db = ProdTimeDeal.objects.filter(portal=self.portal, deal_id=self.deal.deal_id, factory_number__in=mapping.keys())
        for product_in_db in products_in_db:
            fields = creator.build_product_row_add_smart_element(product_in_db)
            queries_for_products_to_smart_elements[f"add_{product_in_db.product_id_b24}"] = {"method": "crm.item.productrow.add", "params": {"fields": fields}}
        logger.info(f'Созданный словарь запросов: {queries_for_products_to_smart_elements=}')
        result = BatchB24(self.portal, queries_for_products_to_smart_elements).results
        logger.info(f'{result=}')
        return result_work

    @staticmethod
    def _make_success_response(result_work: str):
        if not result_work:
            return {
                'result': 'success',
                'info': 'Нет товаров, в которых можно установить заводские номера'
            }
        return {'result': 'success', 'info': result_work}

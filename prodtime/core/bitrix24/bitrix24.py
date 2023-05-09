import datetime

from django.shortcuts import get_object_or_404
from django.utils import timezone
from core.models import Portals
from pybitrix24 import Bitrix24


def create_portal(member_id: str) -> Portals:
    """Метод для создания объекта Портал с проверкой"""

    portal: Portals = get_object_or_404(Portals, member_id=member_id)

    if ((portal.auth_id_create_date + datetime.timedelta(0, 3600)) <
            timezone.now()):
        bx24 = Bitrix24(portal.name)
        bx24.auth_hostname = 'oauth.bitrix.info'
        bx24._refresh_token = portal.refresh_id
        bx24.client_id = portal.client_id
        bx24.client_secret = portal.client_secret
        bx24.refresh_tokens()
        portal.auth_id = bx24._access_token
        portal.refresh_id = bx24._refresh_token
        portal.save()

    return portal


class ObjB24:
    """Базовый класс объекта Битрикс24."""
    GET_PROPS_REST_METHOD: str = ''

    def __init__(self, portal: Portals, id_obj: int):
        self.portal = portal
        self.bx24 = Bitrix24(portal.name)
        self.bx24._access_token = portal.auth_id
        self.id = id_obj
        if self.GET_PROPS_REST_METHOD and self.id:
            self.properties = self._get_properties()

    def _get_properties(self):
        """Получить свойства объекта."""
        return self._check_error(self.bx24.call(
            self.GET_PROPS_REST_METHOD,
            {'id': self.id}
        ))

    @staticmethod
    def _check_error(result):
        if 'error' in result:
            raise RuntimeError(result['error'], result['error_description'])
        elif 'result' in result:
            return result['result']
        else:
            raise RuntimeError('Error', 'No description error')


class ListEntitiesB24(ObjB24):
    """Класс для получения множества сущностей по фильтру."""
    TYPE_ENTITY = {
        'deal': 'crm.deal.list',
        'item': 'crm.item.list'
    }

    def __init__(self, portal: Portals, filter_entity: dict, type_entity: str,
                 select_entity=None):
        super().__init__(portal, 0)
        self.select_entity = ['*'] if select_entity is None else select_entity
        self.filter = filter_entity
        self.method = self.TYPE_ENTITY.get(type_entity)
        self.entities = (self.get_items_filter_no_start() if
                         type_entity == 'item' else self.get_entities_filter())

    def get_entities_filter(self):
        """Получить сущности по фильтру."""
        result = self.bx24.call(self.method, {'filter': self.filter})
        if 'error' in result:
            raise RuntimeError(result['error'], result['error_description'])
        entities = result.get('result')
        while 'next' in result:
            result = self.bx24.call(self.method, {'filter': self.filter,
                                                  'start': result.get('next')})
            entities += result.get('result')
        return entities

    def get_items_filter(self):
        """Получить сущности по фильтру для item."""
        result = self.bx24.call(self.method, {'entityTypeId': 2,
                                              'filter': self.filter,
                                              'select': self.select_entity})
        if 'error' in result:
            raise RuntimeError(result['error'], result['error_description'])
        entities = result.get('result').get('items')
        while 'next' in result:
            result = self.bx24.call(self.method, {'entityTypeId': 2,
                                                  'filter': self.filter,
                                                  'select': self.select_entity,
                                                  'start': result.get('next')})
            entities += result.get('result').get('items')
        return entities

    def get_items_filter_no_start(self):
        """Получить сущности по фильтру для item."""
        deal_id = 0
        finish = False
        deals = []

        while not finish:
            self.filter['>id'] = deal_id
            result = self.bx24.call(self.method, {'entityTypeId': 2,
                                                  'filter': self.filter,
                                                  'order': {'id': 'ASC'},
                                                  'start': -1})
            if result.get('result').get('items'):
                deal_id = result.get('result').get('items')[-1].get('id')
                deals += result.get('result').get('items')
            else:
                finish = True

        return deals


class ListProductRowsB24(ObjB24):
    """Класс для получения множества товарных позиций по фильтру."""

    def __init__(self, portal: Portals, filter_productrows: dict):
        super().__init__(portal, 0)
        self.filter = filter_productrows
        self.entities = self.get_productrows_filter_no_start()

    def get_productrows_filter(self):
        """Получить сущности по фильтру для item."""
        result = self.bx24.call('crm.item.productrow.list',
                                {'filter': self.filter})
        if 'error' in result:
            raise RuntimeError(result['error'], result['error_description'])
        product_rows = result.get('result').get('productRows')
        while 'next' in result:
            result = self.bx24.call('crm.item.productrow.list',
                                    {'filter': self.filter,
                                     'start': result.get('next')})
            product_rows += result.get('result').get('productRows')
        return product_rows

    def get_productrows_filter_no_start(self):
        """Получить сущности по фильтру для item."""
        productrow_id = 0
        finish = False
        productrows = []

        while not finish:
            self.filter['>id'] = productrow_id
            result = self.bx24.call('crm.item.productrow.list',
                                    {'filter': self.filter, 'order': {'id': 'ASC'}, 'start': -1})
            if result.get('result').get('productRows'):
                productrow_id = result.get('result').get('productRows')[-1].get('id')
                productrows += result.get('result').get('productRows')
            else:
                finish = True

        return productrows


class DealB24(ObjB24):
    """Класс Сделка."""
    GET_PROPS_REST_METHOD: str = 'crm.deal.get'

    def __init__(self, portal: Portals, id_obj: int):
        super().__init__(portal, id_obj)
        self.products = None
        self.responsible = self.properties.get('ASSIGNED_BY_ID')
        self.company_id = self.properties.get('COMPANY_ID')

    def get_all_products(self):
        """Получить все продукты сделки."""
        self.products = self._check_error(self.bx24.call(
            'crm.deal.productrows.get', {'id': self.id}
        ))

    def create(self, title, stage_id, responsible_id):
        """Создать сделку в Битрикс24"""
        return self._check_error(self.bx24.call(
            'crm.deal.add',
            {
                'fields': {
                    'TITLE': title,
                    'STAGE_ID': stage_id,
                    'ASSIGNED_BY_ID': responsible_id,
                }
            }
        ))

    def set_products(self, prods_rows):
        """Добавить товар в сделку в Битрикс24."""
        return self._check_error(self.bx24.call(
            'crm.deal.productrows.set',
            {
                'id': self.id,
                'rows': prods_rows,
            }
        ))

    def send_kp_numbers(self, kp_code, kp_value, kp_last_num_code,
                        kp_last_num_value):
        """Обновить номера КП в сделке."""
        return self._check_error(self.bx24.call(
            'crm.deal.update',
            {
                'id': self.id,
                'fields': {
                    kp_code: kp_value,
                    kp_last_num_code: kp_last_num_value
                }
            }
        ))

    def send_equivalent(self, code_equivalent, value_equivalent):
        """Обновить эквивалент в сделке."""
        return self._check_error(self.bx24.call(
            'crm.deal.update',
            {
                'id': self.id,
                'fields': {
                    code_equivalent: value_equivalent
                }
            }
        ))


class QuoteB24(ObjB24):
    """Класс Предложение."""
    GET_PROPS_REST_METHOD: str = 'crm.quote.get'

    def __init__(self, portal: Portals, id_obj: int):
        super().__init__(portal, id_obj)
        self.products = None
        self.deal_id = self.properties.get('DEAL_ID')
        self.responsible = self.properties.get('ASSIGNED_BY_ID')
        self.company_id = self.properties.get('COMPANY_ID')

    def get_all_products(self):
        """Получить все продукты предложения."""
        self.products = self._check_error(self.bx24.call(
            'crm.quote.productrows.get', {'id': self.id}
        ))

    def update(self, fields):
        """Обновить предложение."""
        return self._check_error(self.bx24.call(
            'crm.quote.update', {'id': self.id, 'fields': fields}
        ))


class TemplateDocB24(ObjB24):
    """Класс Шаблоны и Документы."""

    def __init__(self, portal: Portals, id_obj: int):
        super().__init__(portal, id_obj)
        self.templates = None

    def get_all_templates(self, parent='deal'):
        """Получить список всех шаблонов"""
        self.templates = self._check_error(self.bx24.call(
            'crm.documentgenerator.template.list',
            {
                'filter': {
                    'active': 'Y',
                    'entityTypeId': '2%' if parent == 'deal' else '7'
                }
            }
        )).get('templates')

    def create_docs(self, template_id, parent_id, values, parent='deal'):
        """Сформировать документ по шаблону"""

        method_rest = 'crm.documentgenerator.document.add'
        params = {
            'templateId': template_id,
            'entityTypeId': '2' if parent == 'deal' else '7',
            'entityId': parent_id,
            'values': values,
            'fields': {
                'Table': {
                    'PROVIDER': ('Bitrix\\DocumentGenerator\\DataProvider\\'
                                 'ArrayDataProvider'),
                    'OPTIONS': {
                        'ITEM_NAME': 'Item',
                        'ITEM_PROVIDER': ('Bitrix\\DocumentGenerator\\'
                                          'DataProvider\\HashDataProvider'),
                    }
                }
            }
        }
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)


class CompanyB24(ObjB24):
    """Класс Компания Битрикс24."""
    GET_PROPS_REST_METHOD: str = 'crm.company.get'

    def __init__(self, portal, id_obj: int):
        super().__init__(portal, id_obj)
        self.type = self.properties.get('COMPANY_TYPE')
        self.name = self.properties.get('TITLE')

    def get_inn(self):
        """Метод получения ИНН компании."""
        result = self._check_error(self.bx24.call(
            'crm.requisite.list',
            {'filter': {'ENTITY_ID': self.id}, 'select': ['RQ_INN']}
        ))
        return result[0].get('RQ_INN') if result else None


class ActivityB24(ObjB24):
    """Класс Активити Битрикс24 (действия бизнес-процессов)."""

    def __init__(self, portal, obj_id, code=None):
        super().__init__(portal, obj_id)
        self.code = code

    def get_all_installed(self):
        """Получить все установленные активити на портале."""
        return self._check_error(self.bx24.call('bizproc.activity.list'))

    def install(self, params):
        """Метод установки активити на портал."""
        return self._check_error(self.bx24.call(
            'bizproc.activity.add',
            params
        ))

    def uninstall(self):
        """Метод удаления активити на портале."""
        return self._check_error(self.bx24.call(
            'bizproc.activity.delete',
            {'code': self.code}
        ))


class ProductB24(ObjB24):
    """Класс Товар каталога crm."""
    GET_PROPS_REST_METHOD: str = 'crm.product.get'

    def add_catalog(self):
        """Метод добавления товара в каталог."""
        return self._check_error(self.bx24.call('crm.product.add',
                                                {'fields': self.properties}))


class ProductInCatalogB24(ObjB24):
    """Класс Товар в каталоге."""
    GET_PROPS_REST_METHOD: str = 'catalog.product.get'

    def __init__(self, portal: Portals, obj_id: int):
        super().__init__(portal, obj_id)
        if hasattr(self, 'properties'):
            self.properties = self.properties.get('product')

    def add(self):
        """Метод добавления товара в каталог."""
        method_rest = 'catalog.product.add'
        params = {'fields': self.properties}
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)


class ProductRowB24(ObjB24):
    """Класс Товарной позиции."""
    GET_PROPS_REST_METHOD: str = 'crm.item.productrow.get'

    def __init__(self, portal: Portals, obj_id: int):
        super().__init__(portal, obj_id)
        if hasattr(self, 'properties'):
            self.properties = self.properties.get('productRow')
            self.id_in_catalog = self.properties.get('productId')

    def update(self, product_id):
        """Метод изменения товарной позиции."""
        return self._check_error(self.bx24.call(
            'crm.item.productrow.update',
            {
                'id': product_id,
                'fields': self.properties
            }
        ))

    def update_new(self, fields):
        """Метод изменения товарной позиции."""
        return self._check_error(self.bx24.call(
            'crm.item.productrow.update',
            {
                'id': self.id,
                'fields': fields
            }
        ))

    def add(self, fields):
        """Метод добавления товарной позиции."""
        return self._check_error(self.bx24.call(
            'crm.item.productrow.add',
            {
                'fields': fields
            }
        ))

    def delete(self):
        """Метод удаления товарной позиции."""
        return self._check_error(self.bx24.call(
            'crm.item.productrow.delete',
            {
                'id': self.properties.get('id')
            }
        ))


class SmartProcessB24(ObjB24):
    """Класс Smart процесс."""
    GET_PROPS_REST_METHOD: str = 'crm.type.get'

    def get_all_elements(self):
        """Метод получения всех элементов смарт процесса."""
        return self._check_error(self.bx24.call(
            'crm.item.list',
            {
                'entityTypeId': int(self.properties.get('type').get(
                    'entityTypeId')),
            }
        )).get('items')

    def get_all_products(self, element_id):
        """Получить все товары smart процесса"""
        return self._check_error(self.bx24.call(
            'crm.item.productrow.list',
            {
                'filter': {
                    '=ownerType': "Tb1",
                    "=ownerId": element_id
                }
            }
        )).get('productRows')

    def create_element(self, fields):
        """Метод для создания элемента smart процесса."""
        return self._check_error(self.bx24.call(
            'crm.item.add',
            {
                'entityTypeId': int(self.properties.get('type').get(
                    'entityTypeId')),
                'fields': fields,
            }
        ))

    def update_element(self, id_element, fields):
        """Метод для обновления элемента smart процесса."""
        return self._check_error(self.bx24.call(
            'crm.item.update',
            {
                'entityTypeId': int(self.properties.get('type').get(
                    'entityTypeId')),
                'id': id_element,
                'fields': fields,
            }
        ))


class ListB24(ObjB24):
    """Класс Универсальных списков."""

    def get_element_by_id(self, element_id):
        """Метод получения элемента универсального списка по его id."""
        return self._check_error(self.bx24.call(
            'lists.element.get',
            {
                'IBLOCK_TYPE_ID': 'lists',
                'IBLOCK_ID': self.id,
                'ELEMENT_ID': element_id,
            }
        ))

    def get_element_filter(self, filter_dict):
        """Get element list by filter."""
        return self._check_error(self.bx24.call(
            'lists.element.get',
            {
                'IBLOCK_TYPE_ID': 'lists',
                'IBLOCK_ID': self.id,
                'FILTER': filter_dict,
            }
        ))


class UserB24(ObjB24):
    """Класс Пользователь."""
    GET_PROPS_REST_METHOD: str = 'user.get'


class CatalogSectionB24(ObjB24):
    """Класс секции каталога."""
    GET_PROPS_REST_METHOD: str = 'catalog.section.get'

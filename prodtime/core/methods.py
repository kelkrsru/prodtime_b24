import datetime
import decimal
import json
import logging

from django.core.exceptions import BadRequest
from django.db.models import Max
from django.utils import timezone
from pybitrix24 import Bitrix24

from core.bitrix24.bitrix24 import UserB24, DealB24, ProductRowB24, TaskB24, SmartProcessB24, create_portal
from core.models import TemplateDocFields, Responsible
from dealcard.models import ProdTimeDeal, Deal
from settings.models import SettingsPortal

logger = logging.getLogger(__name__)
SEPARATOR = '*' * 40

codes_values = {
    'ID': ['product_id_b24', 'int'],
    'OWNER_ID': ['deal_id', 'int'],
    'PRODUCT_NAME': ['name', 'str'],
    'PRICE': ['price', 'decimal'],
    'PRICE_EXCLUSIVE': ['price_exclusive', 'decimal'],
    'PRICE_NETTO': ['price_netto', 'decimal'],
    'PRICE_BRUTTO': ['price_brutto', 'decimal'],
    'PRICE_ACCOUNT': ['price_account', 'decimal'],
    'QUANTITY': ['quantity', 'decimal'],
    'MEASURE_CODE': ['measure_code', 'int'],
    'MEASURE_NAME': ['measure_name', 'str'],
    'DISCOUNT_TYPE_ID': ['bonus_type_id', 'int'],
    'DISCOUNT_RATE': ['bonus', 'decimal'],
    'DISCOUNT_SUM': ['bonus_sum', 'decimal'],
    'TAX_RATE': ['tax', 'decimal'],
    'TAX_INCLUDED': ['tax_included', 'bool'],
    'SORT': ['sort', 'int'],
}


def check_request(request):
    """Метод проверки на тип запроса."""
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
    elif request.method == 'GET':
        member_id = request.GET.get('member_id')
    else:
        raise BadRequest

    return member_id


def initial_check(request, entity_type='deal_id'):
    """Метод начальной проверки на тип запроса."""
    auth_id = ''

    if request.method == 'POST':
        member_id: str = request.POST['member_id']
        entity_id: int = int(json.loads(request.POST['PLACEMENT_OPTIONS'])['ID'])
        if 'AUTH_ID' in request.POST:
            auth_id: str = request.POST.get('AUTH_ID')
    elif request.method == 'GET':
        member_id: str = request.GET.get('member_id')
        entity_id: int = int(request.GET.get(entity_type))
    else:
        raise BadRequest

    return member_id, entity_id, auth_id


def initial_check_with_token(request, entity_type='deal_id'):
    """Метод начальной проверки на тип запроса с токеном."""

    if request.method == 'GET' or request.method == 'POST':
        member_id = request.GET.get('member_id')
        entity_id = int(request.GET.get(entity_type))
        token = request.GET.get('token')
    else:
        raise BadRequest

    return member_id, entity_id, token


def get_current_user(request, auth_id, portal, is_admin_code):
    """Метод получения текущего пользователя."""
    user_id = 0

    if auth_id:
        bx24_for_user = Bitrix24(portal.name)
        bx24_for_user._access_token = auth_id
        user_result = bx24_for_user.call('user.current')
        if 'result' in user_result:
            user_id = user_result.get('result').get('ID')
    elif 'user_id' in request.COOKIES and request.COOKIES.get('user_id'):
        user_id = request.COOKIES.get('user_id')
    else:
        return {
            'user_id': 0,
            'name': 'Анонимный',
            'lastname': 'пользователь',
            'photo': None,
            'is_admin': 'N',
        }

    user = UserB24(portal, int(user_id))
    return {
        'user_id': user_id,
        'name': user.properties[0].get('NAME'),
        'lastname': user.properties[0].get('LAST_NAME'),
        'photo': user.properties[0].get('PERSONAL_PHOTO'),
        'is_admin': user.properties[0].get(is_admin_code),
    }


def get_responsible_deal(portal, deal_b24):
    """Метод получения ответственного за сделку и создания его в БД приложения."""

    responsible_id = int(deal_b24.responsible)
    responsible_b24 = UserB24(portal, responsible_id)
    responsible, created = Responsible.objects.update_or_create(
        id_b24=responsible_id,
        defaults={
            'first_name': responsible_b24.properties[0].get('NAME'),
            'last_name': responsible_b24.properties[0].get('LAST_NAME'),
            'position': responsible_b24.properties[0].get('WORK_POSITION'),
        },
    )
    return responsible


def calculation_income(products, settings, is_change=True):
    """Метод для расчета прибыли."""

    def _calculation(prod_sum, income_percent):
        return round(prod_sum * (1 - 1 / (1 + income_percent / 100)), 2)

    if hasattr(products, '__iter__'):
        for product in products:
            product.income = _calculation(product.sum, settings.income_percent)
            product.is_change_income = is_change
            product.save()
    else:
        products.income = _calculation(products.sum, settings.income_percent)
        logger.info(f'Для свойства income установлено значение {products.income}')
        products.is_change_income = is_change
        logger.info(f'Для свойства is_change_income установлено значение True')
        products.save()


def update_kp_numbers_in_deal_b24(portal, settings, deal_id, template_id):
    """Метод для обновления нумерации КП в сделке Битрикс24."""
    if template_id and int(template_id) == settings.template_id:
        deal = DealB24(portal, deal_id)
        kp_numbers_deal = deal.properties.get(settings.kp_code)
        kp_numbers = kp_numbers_deal if kp_numbers_deal else []
        last_kp_number = deal.properties.get(settings.kp_last_num_code)
        next_kp_number = int(last_kp_number) + 1 if last_kp_number else 1
        kp_number = f'{timezone.now().year}-{deal_id}.{next_kp_number}'
        kp_numbers.append(kp_number)
        fields = {settings.kp_code: kp_numbers, settings.kp_last_num_code: next_kp_number}
        deal.update(fields)
    else:
        kp_number = ''
        next_kp_number = None
    return kp_number, next_kp_number


def fill_values_for_create_doc(settings, template_id, products, kp_number):
    """Метод заполнения значений, необходимых для создания документа по выбранному шаблону."""

    fields = TemplateDocFields.objects.values()
    fields = list(fields)
    prods_for_template = list()
    count = 1
    for product in products:
        prods_values = dict()
        # all values has code_db == None
        prods_values['ptProductNumber'] = str(count)
        prods_values['ptProductPriceBruttoSum'] = str(round(product['price_brutto'] * product['quantity'], 2))
        prods_values['ptProductPriceNettoSum'] = str(round(product['price_netto'] * product['quantity'], 2))
        prods_values['ptProductDiscountTotal'] = str(round(product['bonus_sum'] * product['quantity'], 2))
        prods_values['ptProductDiscountTotalBrutto'] = str(round(product['bonus'] * product['price_brutto']
                                                                 * product['quantity'] / 100, 2))
        count += 1
        for field in fields:
            if field['code_db'] == 'None':
                continue
            if field['code_db'] == 'prod_time' and product[field['code_db']]:
                prods_values[field['code'].strip('{}')] = (product[field['code_db']].strftime('%d.%m.%Y'))
                continue
            if field['code_db'] == 'prod_time' and not product[field['code_db']]:
                prods_values[field['code'].strip('{}')] = 'Не указан'
                continue
            if field['code_db'] == 'count_days':
                if not product[field['code_db']]:
                    prods_values[field['code'].strip('{}')] = '-'
                else:
                    prods_values[field['code'].strip('{}')] = int(round(product['count_days'], 0))
                continue
            prods_values[field['code'].strip('{}')] = str(product[field['code_db']])
        prods_for_template.append(prods_values)

    values = dict()
    for field in fields:
        field_name = field['code'].strip('{}')
        values[field_name] = 'Table.Item.{}'.format(field_name)
    values['ptProductNumber'] = 'Table.Item.ptProductNumber'
    values['ptProductPriceBruttoSum'] = 'Table.Item.ptProductPriceBruttoSum'
    values['ptProductPriceNettoSum'] = 'Table.Item.ptProductPriceNettoSum'
    values['ptProductDiscountTotal'] = 'Table.Item.ptProductDiscountTotal'
    values['ptProductDiscountTotalBrutto'] = 'Table.Item.ptProductDiscountTotalBrutto'
    values['TableIndex'] = 'Table.INDEX'
    values['Table'] = prods_for_template
    values['ptKpNumber'] = kp_number
    if int(template_id) == settings.template_id:
        values['DocumentNumber'] = kp_number

    return values


def del_prodtime_finish_true_and_sum_values(products_id):
    """Метод для удаления объектов, у которых finish = true, а также подсчет суммарных значений заданных полей."""
    i = 0
    name_fields = {'equivalent_count': 0, 'direct_costs': 1, 'direct_costs_fact': 1}
    sum_values = {}
    max_prodtime = datetime.date(1970,1,1)
    for name_field in name_fields.keys():
        sum_values[name_field + '_sum'] = decimal.Decimal(0)

    while i < len(products_id):
        prodtime = ProdTimeDeal.objects.get(pk=products_id[i])
        if prodtime.finish:
            del products_id[i]
        else:
            i += 1
            for name_field, count in name_fields.items():
                if getattr(prodtime, name_field):
                    key = name_field + '_sum'
                    if count:
                        sum_values[key] += getattr(prodtime, name_field) * prodtime.quantity
                    else:
                        sum_values[key] += getattr(prodtime, name_field)
            if prodtime.prod_time and (max_prodtime <= prodtime.prod_time):
                max_prodtime = prodtime.prod_time

    return products_id, sum_values, max_prodtime


def create_shipment_element(portal, settings, deal_id, products_id, type_elem='deal'):
    """Создать элемент отгрузки."""
    logger.info(f'Запущено создание элемента отгрузки с типом {type_elem=}')
    if type_elem == 'deal':
        sett_create = 'create_deal'
        sett_ru = 'Сделка'
        sett_ru_rod = 'Сделки'
    elif type_elem == 'smart':
        sett_create = 'create_smart'
        sett_ru = 'Элемент смарт процесса'
        sett_ru_rod = 'Элемента смарт процесса'
    else:
        logger.error(f'В функцию create_shipment_element передан неверный тип элемента отгрузки')
        logger.info(SEPARATOR)
        return {'result': 'msg', 'info': f'В функцию create_shipment_element передан неверный тип элемента отгрузки'}

    if not getattr(settings, sett_create):
        logger.info(f'Создание {sett_ru_rod} отключено в настройках. {sett_ru} не создан.')
        logger.info(SEPARATOR)
        return {'result': 'msg', 'info': f'Создание {sett_ru_rod} отключено в настройках. {sett_ru} не создан.'}
    products_id, sum_values, max_prodtime = del_prodtime_finish_true_and_sum_values(products_id)
    if not products_id:
        logger.warning(f'В приложении не выбраны товары: {products_id=}')
        logger.info(SEPARATOR)
        return {'result': 'msg', 'info': 'Вы не выбрали товары.'}
    try:
        deal_bx = DealB24(portal, deal_id)
        logger.debug(f'Реальная сделка: {deal_bx=}')
        if type_elem == 'deal':
            fields_deal = {
                'TITLE': settings.name_deal.replace('{DealId}', str(deal_id)),
                'CATEGORY_ID': settings.category_id,
                'STAGE_ID': settings.stage_code,
                'ASSIGNED_BY_ID': deal_bx.responsible,
                settings.real_deal_code: deal_id,
                'COMPANY_ID': deal_bx.company_id,
                'CONTACT_ID': deal_bx.contact_id,
                settings.sum_equivalent_code: str(sum_values.get('equivalent_count_sum')),
                settings.sum_direct_costs_code: str(sum_values.get('direct_costs_sum')),
                settings.sum_direct_costs_fact_code: str(sum_values.get('direct_costs_fact_sum')),
            }
            logger.debug(f'Поля для создания сделки отгрузки: {fields_deal=}')
            new_elem_id = deal_bx.create(fields_deal)
            logger.debug(f'Созданная сделка отгрузки: {new_elem_id=}')
        elif type_elem == 'smart':
            smart_process = SmartProcessB24(portal, 16)
            logger.debug(f'Смарт процесс: {smart_process=}')
            fields_smart = {
                'title': settings.name_smart,
                'stageId': settings.stage_smart,
                'assignedById': deal_bx.responsible,
                settings.real_deal_code_smart: deal_id,
                'companyId': deal_bx.company_id,
                'contactId': deal_bx.contact_id,
                settings.sum_equivalent_code_smart: str(sum_values.get('equivalent_count_sum')),
                settings.sum_direct_costs_code_smart: str(sum_values.get('direct_costs_sum')),
                settings.sum_direct_costs_fact_code_smart: str(sum_values.get('direct_costs_fact_sum')),
            }
            if max_prodtime != datetime.date(1970,1,1):
                fields_smart[settings.max_prodtime_smart] = str(max_prodtime)
            logger.debug(f'Поля для создания элемента смарт процесса отгрузки: {fields_smart=}')
            new_elem = smart_process.create_element(fields_smart).get('item')
            new_elem_id = new_elem.get('id')
            logger.debug(f'Созданный элемент смарт процесса отгрузки: {new_elem=}')
        else:
            new_elem_id = 0
    except RuntimeError as ex:
        logger.error(f'Ошибка: {ex.args[0]}, Описание ошибки: {ex.args[1]}')
        logger.info(SEPARATOR)
        return {'result': 'msg', 'info': f'Ошибка: {ex.args[0]}, Описание ошибки: {ex.args[1]}'}

    logger.info(f'Добавляем товары в созданный элемент отгрузки')
    for product_id in products_id:
        prodtime = ProdTimeDeal.objects.get(pk=product_id)
        prod_row = ProductRowB24(portal, prodtime.product_id_b24)
        logger.debug(f'Полученный товар из каталога Б24: {prod_row=}')
        if type_elem == 'smart':
            prod_row.properties['ownerType'] = settings.code_smart
        prod_row.properties['ownerId'] = new_elem_id
        del prod_row.properties['id']
        prod_row.add(prod_row.properties)
        logger.info(f'Товар {prod_row.properties["productName"]} добавлен в созданный элемент отгрузки')

    logger.info(SEPARATOR)
    return {'result': 'success', 'info': new_elem_id}


def save_finish(products_id):
    for product_id in products_id:
        prodtime = ProdTimeDeal.objects.get(pk=product_id)
        prodtime.finish = True
        prodtime.save()
        logger.info(f'В БД приложения сохранили признак Выпущен для товара {prodtime.id=}, {prodtime.name_for_print=}')
    logger.info(SEPARATOR)


def create_shipment_task(portal, settings, deal_id):
    """Создать задачу отгрузки."""
    if not settings.create_task:
        return {'result': 'msg', "info": 'Создание задачи отключено в настройках. Задача не создана.'}
    if not deal_id:
        return {'result': 'msg', "info": 'Задача не может быть создана, т.к. сделка не была создана.'}
    deal_bx = DealB24(portal, deal_id)
    deadline = settings.task_deadline
    deadline = timezone.now() + timezone.timedelta(days=deadline)
    fields = {
        'TITLE': settings.name_task.replace('{ProductName}', '').replace('{DealId}', str(deal_bx.id)),
        'RESPONSIBLE_ID': deal_bx.responsible,
        'UF_CRM_TASK': [f'D_{deal_bx.id}'],
        'DEADLINE': deadline.isoformat(),
        'MATCH_WORK_TIME': 'Y',
    }
    bx24_task = TaskB24(portal, 0)
    task_id = bx24_task.create(fields).get('result').get('task').get('id')

    return {'result': 'res', "info": task_id}


def count_sum_equivalent(products):
    """Метод подсчета суммарного эквивалента с учетом количества и скидок"""
    sum_equivalent = 0
    for product in products:
        if product.equivalent_count:
            sum_equivalent += product.equivalent_count * (1 - product.bonus / 100)
    return round(sum_equivalent, 4)


def count_set_max_prodtime(member_id, deal_id):
    """Метод для вычисления и установки максимального срока производства."""
    portal = create_portal(member_id)
    settings_portal = SettingsPortal.objects.get(portal=portal)
    deal = Deal.objects.get(deal_id=deal_id)
    products_for_max = ProdTimeDeal.objects.filter(portal=portal, deal_id=deal_id, prod_time__isnull=False)
    if products_for_max:
        max_prodtime = products_for_max.aggregate(Max('prod_time')).get('prod_time__max')
        deal.max_prodtime = max_prodtime
        deal.save()
    else:
        max_prodtime = 'Не задан'
    deal_bx = DealB24(portal=portal, id_obj=deal_id)
    fields = {settings_portal.max_prodtime_code: max_prodtime.isoformat() if type(max_prodtime) != str else ''}
    deal_bx.update(fields)
    return max_prodtime


def set_fields_from_catalog_b24(product, settings_portal, product_in_catalog):
    """Метод для установки значений полей, значения которых берутся из каталога товаров Битрикс24"""
    name_fields = ['direct_costs', 'standard_hours', 'materials', 'prodtime_str']
    for name_field in name_fields:
        if getattr(product, 'is_change_' + name_field):
            logger.info(f'Свойство is_change_{name_field}=True. Пропускаем.')
            continue
        else:
            code_field = getattr(settings_portal, name_field + '_code')
            value_field = product_in_catalog.properties.get(code_field)
            if type(value_field) is dict and 'value' in value_field:
                if name_field == 'prodtime_str':
                    value = value_field.get('value')
                else:
                    value = round(decimal.Decimal(value_field.get('value')), 2)
                setattr(product, name_field, value)
            else:
                setattr(product, name_field, '' if type(getattr(product, name_field)) == str else 0)
        logger.info(f'Для свойства {name_field} установлено значение {getattr(product, name_field)}')
        product.save()

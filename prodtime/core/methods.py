import decimal
import json

from django.core.exceptions import BadRequest
from django.utils import timezone
from pybitrix24 import Bitrix24

from core.bitrix24.bitrix24 import UserB24, DealB24, ProductRowB24, TaskB24
from core.models import TemplateDocFields
from dealcard.models import ProdTimeDeal


def initial_check(request, entity_type='deal_id'):
    """Метод начальной проверки на тип запроса."""
    auth_id = ''

    if request.method == 'POST':
        member_id: str = request.POST['member_id']
        entity_id: int = int(json.loads(
            request.POST['PLACEMENT_OPTIONS'])['ID'])
        if 'AUTH_ID' in request.POST:
            auth_id: str = request.POST.get('AUTH_ID')
    elif request.method == 'GET':
        member_id: str = request.GET.get('member_id')
        entity_id: int = int(request.GET.get(entity_type))
    else:
        raise BadRequest

    return member_id, entity_id, auth_id


def get_current_user(request, auth_id, portal, is_admin_code):
    """Метод получения текущего пользователя."""
    user_id = 0
    print(auth_id)

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
        products.is_change_income = is_change
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


def del_prodtime_finish_true_and_sum_equivalent(products_id):
    """Метод для удаления объектов, у которых finish = false, а также подсчет суммарных значений заданных полей."""
    i = 0
    name_fields = ['equivalent_count', 'direct_costs', 'direct_costs_fact',]
    sum_values = {}
    for name_field in name_fields:
        sum_values[name_field + '_sum'] = decimal.Decimal(0)

    while i < len(products_id):
        prodtime = ProdTimeDeal.objects.get(pk=products_id[i])
        if prodtime.finish:
            del products_id[i]
        else:
            i += 1
            for name_field in name_fields:
                if getattr(prodtime, name_field):
                    key = name_field + '_sum'
                    sum_values[key] += getattr(prodtime, name_field)

    return products_id, sum_values


def create_shipment_deal(portal, settings, deal_id, products_id):
    """Создать сделку отгрузки."""
    if not settings.create_deal:
        return {'result': 'msg', 'info': 'Создание сделки отключено в настройках. Сделка и задача не созданы.'}
    products_id, sum_values = del_prodtime_finish_true_and_sum_equivalent(products_id)
    if not products_id:
        return {'result': 'msg', 'info': 'Вы не выбрали товары.'}

    try:
        deal_bx = DealB24(portal, deal_id)
        fields = {
            'TITLE': settings.name_deal.replace('{ProductName}', '').replace('{DealId}', str(deal_id)),
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
        new_deal_id = deal_bx.create(fields)
    except RuntimeError as ex:
        return {'result': 'msg', 'info': f'Ошибка: {ex.args[0]}, Описание ошибки: {ex.args[1]}'}

    for product_id in products_id:
        prodtime = ProdTimeDeal.objects.get(pk=product_id)
        prodtime.finish = True
        prodtime.save()

        prod_row = ProductRowB24(portal, prodtime.product_id_b24)
        prod_row.properties['ownerId'] = new_deal_id
        del prod_row.properties['id']
        prod_row.add(prod_row.properties)

    return {'result': 'res', 'info': deal_bx}


def create_shipment_task(portal, settings, deal_bx):
    """Создать задачу отгрузки."""
    if not settings.create_task:
        return {'result': 'msg', "info": 'Создание задачи отключено в настройках. Сделка создана успешно.'}
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
    bx24_task.create(fields)

    return {'result': 'msg', "info": 'Сделка и задача созданы успешно.'}

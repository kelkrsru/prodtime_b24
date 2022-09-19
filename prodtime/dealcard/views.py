import datetime
import decimal
import json

from typing import Dict, Any

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from openpyxl import Workbook
from openpyxl.styles import Alignment

from core.models import Portals, TemplateDocFields
from settings.models import SettingsPortal
from .models import ProdTimeDeal

from pybitrix24 import Bitrix24


@xframe_options_exempt
@csrf_exempt
def index(request):
    """Метод страницы Карточка сделки."""
    template: str = 'dealcard/index.html'
    title: str = 'Страница карточки сделки'

    if request.method == 'POST':
        member_id: str = request.POST['member_id']
        deal_id: int = int(json.loads(request.POST['PLACEMENT_OPTIONS'])['ID'])
    elif request.method == 'GET':
        member_id: str = request.GET.get('member_id')
        deal_id: int = int(request.GET.get('deal_id'))
    else:
        return render(request, 'error.html', {
            'error_name': 'QueryError',
            'error_description': 'Неизвестный тип запроса'
        })

    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    try:
        bx24_deal = DealB24(deal_id, portal)
        bx24_deal.get_deal_products()
        bx24_templates = TemplateDocB24(portal)
        result_templs = bx24_templates.get_all_templates()['templates']
        templates = []
        for templ in result_templs:
            templates.append({
                'id': result_templs[templ]['id'],
                'name': result_templs[templ]['name']
            })
    except RuntimeError as ex:
        return render(request, 'error.html', {
            'error_name': ex.args[0],
            'error_description': ex.args[1]
        })

    products = []
    for product in bx24_deal.deal_products:
        product_value: Dict[str, Any] = {
            'product_id_b24': int(product['ID']),
            'name': product['PRODUCT_NAME'],
            'name_for_print': product['PRODUCT_NAME'],
            'price': round(decimal.Decimal(product['PRICE']), 2),
            'price_acc': round(decimal.Decimal(product['PRICE_ACCOUNT']), 2),
            'price_exs': round(decimal.Decimal(product['PRICE_EXCLUSIVE']), 2),
            'price_netto': round(decimal.Decimal(product['PRICE_NETTO']), 2),
            'price_brutto': round(decimal.Decimal(product['PRICE_BRUTTO']), 2),
            'quantity': round(decimal.Decimal(product['QUANTITY']), 2),
            'measure_code': int(product['MEASURE_CODE']),
            'measure_name': product['MEASURE_NAME'],
            'bonus_type_id': int(product['DISCOUNT_TYPE_ID']),
            'bonus': round(decimal.Decimal(product['DISCOUNT_RATE']), 2),
            'bonus_sum': round(decimal.Decimal(product['DISCOUNT_SUM']), 2),
            'tax': round(decimal.Decimal(product['TAX_RATE']), 2),
            'tax_included': True if product['TAX_INCLUDED'] == 'Y' else False,
        }
        product_value['tax_sum'] = round(product_value['quantity'] *
                                         product_value['price_exs'] *
                                         product_value['tax'] / 100, 2)
        product_value['sum'] = round(product_value['quantity']
                                     * product_value['price_acc'], 2)
        try:
            prodtime: ProdTimeDeal = ProdTimeDeal.objects.get(
                product_id_b24=product_value['product_id_b24']
            )
            product_value['name_for_print'] = prodtime.name_for_print
            product_value['prod_time'] = prodtime.prod_time
            product_value['count_days'] = str(prodtime.count_days).replace(',',
                                                                           '.')
            product_value['finish'] = prodtime.finish
            product_value['id'] = prodtime.pk
            prodtime.name = product_value['name']
            prodtime.price = product_value['price']
            prodtime.price_account = product_value['price_acc']
            prodtime.price_exclusive = product_value['price_exs']
            prodtime.price_netto = product_value['price_netto']
            prodtime.price_brutto = product_value['price_brutto']
            prodtime.quantity = product_value['quantity']
            prodtime.measure_code = product_value['measure_code']
            prodtime.measure_name = product_value['measure_name']
            prodtime.bonus_type_id = product_value['bonus_type_id']
            prodtime.bonus = product_value['bonus']
            prodtime.bonus_sum = product_value['bonus_sum']
            prodtime.tax = product_value['tax']
            prodtime.tax_included = product_value['tax_included']
            prodtime.tax_sum = product_value['tax_sum']
            prodtime.sum = product_value['sum']
            prodtime.save()
        except ObjectDoesNotExist:
            prodtime: ProdTimeDeal = ProdTimeDeal.objects.create(
                product_id_b24=product_value['product_id_b24'],
                name=product_value['name'],
                name_for_print=product_value['name_for_print'],
                price=product_value['price'],
                price_account=product_value['price_acc'],
                price_exclusive=product_value['price_exs'],
                price_netto=product_value['price_netto'],
                price_brutto=product_value['price_brutto'],
                quantity=product_value['quantity'],
                measure_code=product_value['measure_code'],
                measure_name=product_value['measure_name'],
                bonus_type_id=product_value['bonus_type_id'],
                bonus=product_value['bonus'],
                bonus_sum=product_value['bonus_sum'],
                tax=product_value['tax'],
                tax_included=product_value['tax_included'],
                tax_sum=product_value['tax_sum'],
                sum=product_value['sum'],
                deal_id=deal_id,
                portal=portal,
            )
            product_value['id'] = prodtime.pk

        # Работа с эквивалентом
        if prodtime.is_change_equivalent:
            product_value['equivalent'] = str(prodtime.equivalent).replace(
                ',', '.')
        else:
            product_in_catalog = ProductB24(portal,
                                            prodtime.product_id_b24)
            equivalent_code = settings_portal.equivalent_code
            if (not product_in_catalog.props
                    or equivalent_code not in product_in_catalog.props
                    or not product_in_catalog.props.get(equivalent_code)):
                product_value['equivalent'] = ''
                prodtime.equivalent = 0
            else:
                product_value['equivalent'] = list(
                    product_in_catalog.props.get(
                        equivalent_code).values())[1]
                prodtime.equivalent = decimal.Decimal(
                    product_value['equivalent'])
            prodtime.save()
        if prodtime.equivalent and prodtime.quantity:
            prodtime.equivalent_count = (prodtime.equivalent *
                                         prodtime.quantity)
            prodtime.save()
        products.append(product_value)

    products_in_db = ProdTimeDeal.objects.filter(portal=portal,
                                                 deal_id=deal_id)
    for product in products_in_db:
        if not next((x for x in products if
                     x['product_id_b24'] == product.product_id_b24), None):
            product.delete()

    sum_equivalent = ProdTimeDeal.objects.filter(
        portal=portal, deal_id=deal_id).aggregate(Sum('equivalent_count'))
    sum_equivalent = sum_equivalent['equivalent_count__sum']

    context = {
        'title': title,
        'products': products,
        'sum_equivalent': sum_equivalent,
        'member_id': member_id,
        'deal_id': deal_id,
        'templates': templates,
    }
    return render(request, template, context)


@xframe_options_exempt
@csrf_exempt
def save(request):
    """Метод для сохранения изменений в таблице."""

    product_id = request.POST.get('id')
    type_field = request.POST.get('type')
    value = request.POST.get('value')

    prodtime: ProdTimeDeal = get_object_or_404(ProdTimeDeal, pk=product_id)
    if type_field == 'name-for-print':
        prodtime.name_for_print = value
    if type_field == 'prod-time':
        prodtime.prod_time = value
    if type_field == 'count-days':
        prodtime.count_days = value
    if type_field == 'equivalent':
        if value:
            prodtime.equivalent = value
            prodtime.equivalent_count = (decimal.Decimal(value)
                                         * prodtime.quantity)
            prodtime.is_change_equivalent = True
    if type_field == 'finish':
        if value == 'true':
            prodtime.finish = True
        if value == 'false':
            prodtime.finish = False
    prodtime.save()

    return JsonResponse({"success": "Updated"})


@xframe_options_exempt
@csrf_exempt
def create(request):
    """Метод создания задачи и сделки."""

    products_id = request.POST.getlist('products_id[]')
    member_id = request.POST.get('member_id')
    deal_id = request.POST.get('deal_id')
    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    if not settings_portal.create_deal:
        return JsonResponse({
            'result': 'nodeal',
            "info": ('Создание сделки отключено в настройках. Сделка и задача'
                     ' не созданы.')
        })

    i = 0
    while i < len(products_id):
        prodtime: ProdTimeDeal = get_object_or_404(ProdTimeDeal,
                                                   pk=products_id[i])
        if prodtime.finish:
            del products_id[i]
        else:
            i += 1
    if not products_id:
        return JsonResponse({
            'result': 'noproducts',
            "info": ('Вы не выбрали товары.')
        })

    try:
        bx24_deal = DealB24(deal_id, portal)
        bx24_deal.get_deal_responsible()
        bx24_deal.get_deal_company()
        title_new_deal = (settings_portal.name_deal
                          .replace('{ProductName}', '')
                          .replace('{DealId}', str(deal_id)))
        new_deal_id = bx24_deal.create_deal(
            title_new_deal,
            settings_portal.category_id,
            settings_portal.stage_code,
            bx24_deal.deal_responsible,
            deal_id,
            settings_portal.real_deal_code,
            bx24_deal.deal_company,
            bx24_deal.deal_contact,
        )
    except RuntimeError as ex:
        return render(request, 'error.html', {
            'error_name': ex.args[0],
            'error_description': ex.args[1]
        })

    for product_id in products_id:
        prodtime: ProdTimeDeal = get_object_or_404(ProdTimeDeal, pk=product_id)
        prodtime.finish = True
        prodtime.save()

        prod_row = bx24_deal.get_deal_product_by_id(prodtime.product_id_b24)
        prod_row['ownerId'] = new_deal_id
        del prod_row['id']
        bx24_deal.add_deal_product(prod_row)

    if not settings_portal.create_task:
        return JsonResponse({
            'result': 'notask',
            "info": ('Создание задачи отключено в настройках. Сделка '
                     'создана успешно.')
        })
    bx24_task = TaskB24(portal)
    title_task = (settings_portal.name_task
                  .replace('{ProductName}', '')
                  .replace('{DealId}', str(deal_id)))
    deadline = settings_portal.task_deadline
    bx24_task.create_task(title_task, bx24_deal.deal_responsible,
                          new_deal_id, deadline)

    return JsonResponse({
        'result': 'dealandtask',
        "info": 'Сделка и задача созданы успешно.'
    })


@xframe_options_exempt
@csrf_exempt
def create_doc(request):
    """Метод создания документа по выбранному шаблону."""

    member_id = request.POST.get('member_id')
    template_id = request.POST.get('templ_id')
    deal_id = int(request.POST.get('deal_id'))
    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    if int(template_id) == settings_portal.template_id:
        try:
            deal = DealB24(deal_id, portal)
            res = deal.get_deal_kp_numbers()
            kp_code = settings_portal.kp_code
            kp_last_num_code = settings_portal.kp_last_num_code
            kp_numbers_deal = res[kp_code]
            kp_numbers = kp_numbers_deal if kp_numbers_deal else []
            last_kp_number = res[kp_last_num_code]
            next_kp_number = int(last_kp_number) + 1 if last_kp_number else 1
            kp_number = f'{timezone.now().year}-{deal_id}.{next_kp_number}'
            kp_numbers.append(kp_number)
            deal.send_kp_numbers(kp_code, kp_numbers, kp_last_num_code,
                                 next_kp_number)
        except RuntimeError as ex:
            return render(request, 'error.html', {
                'error_name': ex.args[0],
                'error_description': ex.args[1]
            })
    else:
        kp_number = ''

    products = ProdTimeDeal.objects.filter(portal=portal,
                                           deal_id=deal_id).values()
    fields = TemplateDocFields.objects.values()
    fields = list(fields)
    prods_for_template = list()
    count = 1
    for product in products:
        prods_values = dict()
        prods_values['ptProductNumber'] = str(count)  # code_db == None
        prods_values['ptProductPriceBruttoSum'] = str(
            round(product['price_brutto'] * product['quantity'], 2)
        )  # code_db == None
        prods_values['ptProductPriceNettoSum'] = str(
            round(product['price_netto'] * product['quantity'], 2)
        )  # code_db == None
        prods_values['ptProductDiscountTotal'] = str(
            round(product['bonus_sum'] * product['quantity'], 2)
        )  # code_db == None
        prods_values['ptProductDiscountTotalBrutto'] = str(
            round(product['bonus'] * product['price_brutto']
                  * product['quantity'] / 100, 2)
        )  # code_db == None
        count += 1
        for field in fields:
            if field['code_db'] == 'None':
                continue
            if field['code_db'] == 'prod_time' and product[field['code_db']]:
                prods_values[field['code'].strip('{}')] = (
                    product[field['code_db']].strftime('%d.%m.%Y'))
                continue
            if (field['code_db'] == 'prod_time'
                    and not product[field['code_db']]):
                prods_values[field['code'].strip('{}')] = 'Не указан'
                continue
            if field['code_db'] == 'count_days':
                if not product[field['code_db']]:
                    prods_values[field['code'].strip('{}')] = '-'
                else:
                    prods_values[field['code'].strip('{}')] = int(
                        round(product['count_days'], 0))
                continue
            prods_values[field['code'].strip('{}')] = str(
                product[field['code_db']])
        prods_for_template.append(prods_values)

    values = dict()
    for field in fields:
        field_name = field['code'].strip('{}')
        values[field_name] = 'Table.Item.{}'.format(field_name)
    values['ptProductNumber'] = 'Table.Item.ptProductNumber'
    values['ptProductPriceBruttoSum'] = 'Table.Item.ptProductPriceBruttoSum'
    values['ptProductPriceNettoSum'] = 'Table.Item.ptProductPriceNettoSum'
    values['ptProductDiscountTotal'] = 'Table.Item.ptProductDiscountTotal'
    values['ptProductDiscountTotalBrutto'] = (
        'Table.Item.ptProductDiscountTotalBrutto')
    values['TableIndex'] = 'Table.INDEX'
    values['Table'] = prods_for_template
    values['ptKpNumber'] = kp_number
    if int(template_id) == settings_portal.template_id:
        values['DocumentNumber'] = kp_number

    try:
        bx24_template_doc = TemplateDocB24(portal)
        result = bx24_template_doc.create_docs(template_id, deal_id, values)
    except RuntimeError as ex:
        return render(request, 'error.html', {
            'error_name': ex.args[0],
            'error_description': ex.args[1]
        })

    return JsonResponse({'result': result})


@xframe_options_exempt
@csrf_exempt
def copy_products(request):
    """Метод копирования товаров в каталог и сделку."""

    member_id = request.POST.get('member_id')
    deal_id = int(request.POST.get('deal_id'))
    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    result_copy = 'error'
    products = ProdTimeDeal.objects.filter(portal=portal, deal_id=deal_id)

    for product in products:
        if product.name == product.name_for_print:
            continue
        try:
            product_in_catalog = ProductB24(portal, product.product_id_b24)
            section_id = product_in_catalog.props.get('SECTION_ID')
            element_list = ListsB24(portal, settings_portal.section_list_id)
            element_list.get_element_by_filter(
                section_id, settings_portal.real_section_code)
            if not element_list.element_props:
                new_section_id = settings_portal.default_section_id
            else:
                new_section_id = list(
                    element_list.element_props[0].get(
                        settings_portal.copy_section_code).values())[0]
            if product.is_change_equivalent:
                product_in_catalog.props[settings_portal.equivalent_code] = {}
                product_in_catalog.props[settings_portal.equivalent_code][
                    'value'] = str(product.equivalent)
            product_in_catalog.props['NAME'] = product.name_for_print
            product_in_catalog.props['SECTION_ID'] = new_section_id
            del product_in_catalog.props['ID']
            new_id_product_in_catalog = product_in_catalog.add_catalog()
            product_in_catalog.productrow[
                'productId'] = new_id_product_in_catalog
            product_in_catalog.productrow[
                'productName'] = product.name_for_print
            del product_in_catalog.productrow['id']
            result = product_in_catalog.update(product.product_id_b24)
            if 'productRow' in result:
                result_copy = 'ok'

        except RuntimeError as ex:
            return render(request, 'error.html', {
                'error_name': ex.args[0],
                'error_description': ex.args[1]
            })

    return JsonResponse({'result': result_copy})


@xframe_options_exempt
@csrf_exempt
def send_equivalent(request):
    """Метод отправки суммарного эквивалента в сделку."""

    member_id = request.POST.get('member_id')
    deal_id = int(request.POST.get('deal_id'))
    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    sum_equivalent = ProdTimeDeal.objects.filter(
        portal=portal, deal_id=deal_id).aggregate(Sum('equivalent_count'))
    sum_equivalent = float(sum_equivalent['equivalent_count__sum'])
    deal = DealB24(deal_id, portal)
    deal.send_equivalent(settings_portal.sum_equivalent_code, sum_equivalent)

    return JsonResponse({'result': sum_equivalent})


@xframe_options_exempt
@csrf_exempt
def export_excel(request):
    """Метод экспорта в excel."""

    member_id = request.GET.get('member_id')
    deal_id = int(request.GET.get('deal_id'))
    portal: Portals = _create_portal(member_id)

    products = ProdTimeDeal.objects.filter(portal=portal, deal_id=deal_id)

    try:
        deal = DealB24(deal_id, portal)
        deal.get_deal_company()
        company = CompanyB24(portal, deal.deal_company)
        company.get_name()
        company_name = company.name
    except RuntimeError:
        company_name = 'Не удалось получить наименование компании'

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.'
                     'spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Prodtime'

    columns = [
        'Товар',
        'Кол-во',
        'Кол-во раб. дней',
        'Срок производства'
    ]

    worksheet.merge_cells('B1:D1')
    worksheet.merge_cells('B2:D2')
    worksheet.cell(1, 1).value = 'ИД сделки:'
    worksheet.cell(1, 2).value = deal_id
    worksheet.cell(1, 2).alignment = Alignment(horizontal='left')
    worksheet.cell(2, 1).value = 'Компания сделки:'
    worksheet.cell(2, 2).value = company_name

    row_num = 4
    worksheet.column_dimensions['A'].width = 70
    worksheet.column_dimensions['B'].width = 10
    worksheet.column_dimensions['C'].width = 17
    worksheet.column_dimensions['D'].width = 20

    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title

    for product in products:
        row_num += 1

        row = [
            product.name,
            product.quantity,
            product.count_days,
            product.prod_time,
        ]

        for col_num, cell_value in enumerate(row, 1):
            worksheet.row_dimensions[row_num].height = 30
            cell = worksheet.cell(row=row_num, column=col_num)
            alignment = Alignment(vertical='center', wrap_text=True)
            cell.alignment = alignment
            cell.value = cell_value

    workbook.save(response)

    return response


def _create_portal(member_id: str) -> Portals:
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
    """Класс объекта Битрикс24"""

    def __init__(self, portal: Portals):
        self.portal = portal
        self.bx24 = Bitrix24(portal.name)
        self.bx24._access_token = portal.auth_id

    @staticmethod
    def _check_error(result):
        if 'error' in result:
            raise RuntimeError(result['error'], result['error_description'])
        elif 'result' in result:
            return result['result']
        else:
            raise RuntimeError('Error', 'No description error')


class DealB24(ObjB24):
    """Класс Сделка Битрикс24"""

    def __init__(self, deal_id: int, portal: Portals):
        super(DealB24, self).__init__(portal)
        self.deal_id = deal_id
        self.deal_products = None
        self.deal_responsible = None
        self.deal_company = None
        self.deal_contact = None

    def get_deal_products(self):
        """Получить все продукты сделки"""

        method_rest = 'crm.deal.productrows.get'
        params = {'id': self.deal_id}
        result = self.bx24.call(method_rest, params)
        self.deal_products = self._check_error(result)

    def get_deal_product_by_id(self, product_id):
        """Получить продукт сделки Битрикс24 по ID"""

        method_rest = 'crm.item.productrow.get'
        params = {'id': product_id}
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)['productRow']

    def get_deal_responsible(self):
        """Получить ответственного за сделку."""

        method_rest = 'crm.deal.get'
        params = {'id': self.deal_id}
        result = self.bx24.call(method_rest, params)
        self.deal_responsible = self._check_error(result)['ASSIGNED_BY_ID']

    def get_deal_company(self):
        """Получить компанию сделки."""

        method_rest = 'crm.deal.get'
        params = {'id': self.deal_id}
        result = self.bx24.call(method_rest, params)
        self.deal_company = self._check_error(result)['COMPANY_ID']
        self.deal_contact = self._check_error(result)['CONTACT_ID']

    def get_deal_kp_numbers(self):
        """Получить нумерацию по КП сделки."""

        method_rest = 'crm.deal.get'
        params = {'id': self.deal_id}
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)

    def create_deal(self, title, category_id, stage_id, responsible_id,
                    rel_deal_id, rel_deal_code, company_id, contact_id):
        """Создать сделку в Битрикс24"""

        method_rest = 'crm.deal.add'
        params = {
            'fields': {
                'TITLE': title,
                'CATEGORY_ID': category_id,
                'STAGE_ID': stage_id,
                'ASSIGNED_BY_ID': responsible_id,
                rel_deal_code: rel_deal_id,
                'COMPANY_ID': company_id,
                'CONTACT_ID': contact_id,
            }
        }
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)

    def add_deal_product(self, prod_row):
        """Добавить товар в сделку в Битрикс24"""

        method_rest = 'crm.item.productrow.add'
        params = {
            'fields': prod_row
        }
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)

    def send_equivalent(self, code_equivalent, value_equivalent):
        """Обновить эквивалент в сделке."""

        method_rest = 'crm.deal.update'
        params = {
            'id': self.deal_id,
            'fields': {
                code_equivalent: value_equivalent
            }
        }
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)

    def send_kp_numbers(self, kp_code, kp_value, kp_last_num_code,
                        kp_last_num_value):
        """Обновить номера КП в сделке."""

        method_rest = 'crm.deal.update'
        params = {
            'id': self.deal_id,
            'fields': {
                kp_code: kp_value,
                kp_last_num_code: kp_last_num_value
            }
        }
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)


class TemplateDocB24(ObjB24):
    """Класс Шаблоны и Документы Битрикс24"""

    def get_all_templates(self):
        """Получить список всех шаблонов"""

        method_rest = 'crm.documentgenerator.template.list'
        params = {
            'filter': {
                'active': 'Y',
                'entityTypeId': '2%'
            }
        }
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)

    def create_docs(self, template_id, deal_id, values):
        """Сформировать документ по шаблону"""

        method_rest = 'crm.documentgenerator.document.add'
        params = {
            'templateId': template_id,
            'entityTypeId': '2',
            'entityId': deal_id,
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

    def __init__(self, portal, company_id=None):
        super(CompanyB24, self).__init__(portal)
        self.id = company_id
        self.name = None

    def get_name(self):
        """Получить тип компании в Битрикс24."""
        method_rest = 'crm.company.get'
        params = {'id': self.id}
        result = self.bx24.call(method_rest, params)
        self.name = (self._check_error(result))['TITLE']


class TaskB24(ObjB24):
    """Класс Задача Битрикс24."""

    def create_task(self, title, responsible_id, deal_id, deadline):
        """Создать задачу в Битрикс24"""

        deadline = timezone.now() + timezone.timedelta(days=deadline)

        method_rest = 'tasks.task.add'
        params = {
            'fields': {
                'TITLE': title,
                'RESPONSIBLE_ID': responsible_id,
                'UF_CRM_TASK': [f'D_{deal_id}'],
                'DEADLINE': deadline.isoformat(),
                'MATCH_WORK_TIME': 'Y',
            }
        }
        result = self.bx24.call(method_rest, params)
        return result


class ProductB24(ObjB24):
    """Класс товара каталога Битрикс24."""

    def __init__(self, portal, product_id):
        super(ProductB24, self).__init__(portal)
        self.id = product_id
        self.productrow = None
        self.id_catalog = self.get_product_catalog_id()
        self.props = self.get_properties()

    def get_product_catalog_id(self):
        method_rest = 'crm.item.productrow.get'
        params = {'id': self.id}
        result = self.bx24.call(method_rest, params)
        self.productrow = self._check_error(result).get('productRow')
        return self.productrow.get('productId')

    def get_properties(self):
        """Метод получения свойств товара каталога."""
        method_rest = 'crm.product.get'
        params = {'id': self.id_catalog}
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)

    def add_catalog(self):
        """Метод добавления товара в каталог."""
        method_rest = 'crm.product.add'
        params = {'fields': self.props}
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)

    def update(self, product_id):
        """Метод изменения товарной позиции."""
        method_rest = 'crm.item.productrow.update'
        params = {
            'id': product_id,
            'fields': self.productrow
        }
        result = self.bx24.call(method_rest, params)
        return self._check_error(result)


class ListsB24(ObjB24):
    """Class List Bitrix24."""

    def __init__(self, portal, list_id):
        super(ListsB24, self).__init__(portal)
        self.id = list_id
        self.element_props = None

    def get_element_by_filter(self, section_id, real_section_code):
        """Get element list by id."""
        method_rest = 'lists.element.get'
        params = {
            'IBLOCK_TYPE_ID': 'lists',
            'IBLOCK_ID': self.id,
            'FILTER': {
                f'={real_section_code}': [section_id],
            },
        }
        result = self.bx24.call(method_rest, params)
        self.element_props = self._check_error(result)

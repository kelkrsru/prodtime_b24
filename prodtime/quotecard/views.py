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
from dealcard.models import ProdTimeDeal
from settings.models import SettingsPortal
from .models import ProdTimeQuote

from pybitrix24 import Bitrix24
from core.bitrix24.bitrix24 import QuoteB24, TemplateDocB24, ProductB24, \
    CompanyB24, DealB24, ProductRowB24, ListB24


@xframe_options_exempt
@csrf_exempt
def index(request):
    """Метод страницы Карточка предложения."""
    template: str = 'quotecard/index.html'
    title: str = 'Страница карточки сделки'

    if request.method == 'POST':
        member_id: str = request.POST['member_id']
        quote_id: int = int(json.loads(request.POST['PLACEMENT_OPTIONS'])['ID'])
    elif request.method == 'GET':
        member_id: str = request.GET.get('member_id')
        quote_id: int = int(request.GET.get('quote_id'))
    else:
        return render(request, 'error.html', {
            'error_name': 'QueryError',
            'error_description': 'Неизвестный тип запроса'
        })

    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    try:
        quote = QuoteB24(portal, quote_id)
        quote.get_all_products()
        template_doc = TemplateDocB24(portal, 0)
        template_doc.get_all_templates(parent='quote')
        templates = ([{'id': templ['id'], 'name': templ['name']}
                      for templ in template_doc.templates.values()])
    except RuntimeError as ex:
        return render(request, 'error.html', {
            'error_name': ex.args[0],
            'error_description': ex.args[1]
        })

    if not quote.deal_id or int(quote.deal_id) == 0:
        return render(request, 'error.html', {
            'error_name': 'Отсутствует привязка к сделке',
            'error_description': 'Привяжите сделку и обновите страницу.'
        })

    products = []
    for product in quote.products:
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
            'sort': int(product['SORT']),
        }
        product_value['tax_sum'] = round(product_value['quantity'] *
                                         product_value['price_exs'] *
                                         product_value['tax'] / 100, 2)
        product_value['sum'] = round(product_value['quantity']
                                     * product_value['price_acc'], 2)
        try:
            prodtime: ProdTimeQuote = ProdTimeQuote.objects.get(
                product_id_b24=product_value['product_id_b24']
            )
            product_value['name_for_print'] = prodtime.name_for_print
            product_value['prod_time'] = prodtime.prod_time
            product_value['count_days'] = str(prodtime.count_days).replace(',',
                                                                           '.')
            product_value['finish'] = prodtime.finish
            product_value['made'] = prodtime.made
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
            prodtime.sort = product_value['sort']
            prodtime.save()
        except ObjectDoesNotExist:
            prodtime: ProdTimeQuote = ProdTimeQuote.objects.create(
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
                sort=product_value['sort'],
                quote_id=quote_id,
                portal=portal,
            )
            product_value['id'] = prodtime.pk

        # Работа с эквивалентом
        if prodtime.is_change_equivalent:
            product_value['equivalent'] = str(prodtime.equivalent).replace(
                ',', '.')
        else:
            product_in_catalog = ProductB24(portal, product["PRODUCT_ID"])
            equivalent_code = settings_portal.equivalent_code
            if (not product_in_catalog.properties
                    or equivalent_code not in product_in_catalog.properties
                    or not product_in_catalog.properties.get(equivalent_code)):
                product_value['equivalent'] = ''
                prodtime.equivalent = 0
            else:
                product_value['equivalent'] = list(
                    product_in_catalog.properties.get(
                        equivalent_code).values())[1]
                prodtime.equivalent = decimal.Decimal(
                    product_value['equivalent'])
            prodtime.save()
        if prodtime.equivalent and prodtime.quantity:
            prodtime.equivalent_count = (prodtime.equivalent *
                                         prodtime.quantity)
            prodtime.save()
        products.append(product_value)

    products_in_db = ProdTimeQuote.objects.filter(portal=portal, quote_id=quote_id)
    for product in products_in_db:
        if not next((x for x in products if
                     x['product_id_b24'] == product.product_id_b24), None):
            product.delete()

    sum_equivalent = ProdTimeQuote.objects.filter(
        portal=portal, quote_id=quote_id).aggregate(Sum('equivalent_count'))
    sum_equivalent = sum_equivalent['equivalent_count__sum']

    products = sorted(products, key=lambda prod: prod.get('sort'))

    context = {
        'title': title,
        'products': products,
        'sum_equivalent': sum_equivalent,
        'member_id': member_id,
        'quote_id': quote_id,
        'deal_id': int(quote.deal_id),
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

    prodtime: ProdTimeQuote = get_object_or_404(ProdTimeQuote, pk=product_id)
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
    prodtime.save()

    return JsonResponse({"success": "Updated"})


@xframe_options_exempt
@csrf_exempt
def create_doc(request):
    """Метод создания документа по выбранному шаблону."""

    member_id = request.POST.get('member_id')
    template_id = request.POST.get('templ_id')
    quote_id = int(request.POST.get('quote_id'))
    deal_id = int(request.POST.get('deal_id'))
    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    if int(template_id) == settings_portal.template_id:
        try:
            deal = DealB24(portal, deal_id)
            kp_code = settings_portal.kp_code
            kp_last_num_code = settings_portal.kp_last_num_code
            kp_numbers_deal = deal.properties.get(kp_code)
            kp_numbers = kp_numbers_deal if kp_numbers_deal else []
            last_kp_number = deal.properties.get(kp_last_num_code)
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

    products = ProdTimeQuote.objects.filter(portal=portal, quote_id=quote_id).values()
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
                    prods_values[field['code'].strip('{}')] = int(round(product['count_days'], 0))
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
        bx24_template_doc = TemplateDocB24(portal, 0)
        result = bx24_template_doc.create_docs(template_id, quote_id, values, parent='quote')
    except RuntimeError as ex:
        return render(request, 'error.html', {
            'error_name': ex.args[0],
            'error_description': ex.args[1]
        })

    return JsonResponse({'result': result})


@xframe_options_exempt
@csrf_exempt
def copy_products(request):
    """Метод копирования товаров в каталог и предложение."""

    member_id = request.POST.get('member_id')
    quote_id = int(request.POST.get('quote_id'))
    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    result_copy = 'error'
    products = ProdTimeQuote.objects.filter(portal=portal, quote_id=quote_id)

    for product in products:
        if product.name == product.name_for_print:
            continue
        try:
            productrow = ProductRowB24(portal, product.product_id_b24)
            product_in_catalog = ProductB24(portal, productrow.id_in_catalog)
            section_id = product_in_catalog.properties.get('SECTION_ID')
            element_list = ListB24(
                portal, settings_portal.section_list_id).get_element_by_filter(
                section_id, settings_portal.real_section_code)
            if not element_list:
                new_section_id = settings_portal.default_section_id
            else:
                new_section_id = list(
                    element_list[0].get(
                        settings_portal.copy_section_code).values())[0]
            if product.is_change_equivalent:
                product_in_catalog.properties[settings_portal.equivalent_code] = {}
                product_in_catalog.properties[settings_portal.equivalent_code][
                    'value'] = str(product.equivalent)
            product_in_catalog.properties['NAME'] = product.name_for_print
            product_in_catalog.properties['SECTION_ID'] = new_section_id
            del product_in_catalog.properties['ID']
            new_id_product_in_catalog = product_in_catalog.add_catalog()
            productrow.properties['productId'] = new_id_product_in_catalog
            productrow.properties['productName'] = product.name_for_print
            del productrow.properties['id']
            result = productrow.update(product.product_id_b24)
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
    quote_id = int(request.POST.get('quote_id'))
    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    sum_equivalent = ProdTimeQuote.objects.filter(
        portal=portal, quote_id=quote_id).aggregate(Sum('equivalent_count'))
    sum_equivalent = float(sum_equivalent['equivalent_count__sum'])
    deal = DealB24(portal, deal_id)
    deal.send_equivalent(settings_portal.sum_equivalent_code, sum_equivalent)

    return JsonResponse({'result': sum_equivalent})


@xframe_options_exempt
@csrf_exempt
def send_products(request):
    """Метод передачи товаров из предложения в связанную сделку."""
    member_id = request.POST.get('member_id')
    deal_id = int(request.POST.get('deal_id'))
    quote_id = int(request.POST.get('quote_id'))
    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    try:
        quote = QuoteB24(portal, quote_id)
        quote.get_all_products()
        for product in quote.products:
            keys_for_del = ['ID', 'OWNER_ID', 'OWNER_TYPE']
            for key in keys_for_del:
                del product[key]
        deal = DealB24(portal, deal_id)
        deal.set_products(quote.products)
        deal.get_all_products()
        quote.get_all_products()
        ProdTimeDeal.objects.filter(portal=portal, deal_id=deal_id).delete()
        for count, product in enumerate(quote.products):
            prodtime_in_quote = ProdTimeQuote.objects.get(
                portal=portal, quote_id=quote_id,
                product_id_b24=int(product.get('ID')))
            ProdTimeDeal.objects.create(
                product_id_b24=deal.products[count].get('ID'),
                name=prodtime_in_quote.name,
                name_for_print=prodtime_in_quote.name_for_print,
                price=prodtime_in_quote.price,
                price_account=prodtime_in_quote.price_account,
                price_exclusive=prodtime_in_quote.price_exclusive,
                price_netto=prodtime_in_quote.price_netto,
                price_brutto=prodtime_in_quote.price_brutto,
                quantity=prodtime_in_quote.quantity,
                measure_code=prodtime_in_quote.measure_code,
                measure_name=prodtime_in_quote.measure_name,
                bonus_type_id=prodtime_in_quote.bonus_type_id,
                bonus=prodtime_in_quote.bonus,
                bonus_sum=prodtime_in_quote.bonus_sum,
                tax=prodtime_in_quote.tax,
                tax_included=prodtime_in_quote.tax_included,
                tax_sum=prodtime_in_quote.tax_sum,
                sum=prodtime_in_quote.sum,
                sort=prodtime_in_quote.sort,
                deal_id=deal.id,
                equivalent=prodtime_in_quote.equivalent,
                equivalent_count=prodtime_in_quote.equivalent_count,
                is_change_equivalent=prodtime_in_quote.is_change_equivalent,
                prod_time=prodtime_in_quote.prod_time,
                count_days=prodtime_in_quote.count_days,
                portal=portal,
            )
    except RuntimeError as ex:
        return render(request, 'error.html', {
            'error_name': ex.args[0],
            'error_description': ex.args[1]
        })

    sum_equivalent = ProdTimeDeal.objects.filter(
        portal=portal, deal_id=deal_id).aggregate(Sum('equivalent_count'))
    sum_equivalent = float(sum_equivalent['equivalent_count__sum'])
    deal.send_equivalent(settings_portal.sum_equivalent_code, sum_equivalent)

    return JsonResponse({'result': 'ok'})

@xframe_options_exempt
@csrf_exempt
def export_excel(request):
    """Метод экспорта в excel."""

    member_id = request.GET.get('member_id')
    quote_id = int(request.GET.get('quote_id'))
    portal: Portals = _create_portal(member_id)

    products = ProdTimeQuote.objects.filter(portal=portal, quote_id=quote_id)
    products = sorted(products, key=lambda prod: prod.sort)

    try:
        quote = QuoteB24(portal, quote_id)
        company = CompanyB24(portal, quote.company_id)
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
    worksheet.cell(1, 1).value = 'ИД предложения:'
    worksheet.cell(1, 2).value = quote_id
    worksheet.cell(1, 2).alignment = Alignment(horizontal='left')
    worksheet.cell(2, 1).value = 'Компания предложения:'
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
            product.prod_time.strftime('%d.%m.%Y'),
        ]

        for col_num, cell_value in enumerate(row, 1):
            worksheet.row_dimensions[row_num].height = 30
            cell = worksheet.cell(row=row_num, column=col_num)
            alignment = Alignment(vertical='center', wrap_text=True, horizontal='left')
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

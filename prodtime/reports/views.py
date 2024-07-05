import decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from core.bitrix24.bitrix24 import (create_portal, ListEntitiesB24,
                                    ListProductRowsB24, ProductInCatalogB24,
                                    CatalogSectionB24)
from core.methods import get_current_user
from core.models import Portals
from dealcard.models import ProdTimeDeal, Deal
from reports.forms import ReportDealsForm, ReportProductionForm
from settings.models import SettingsPortal


@xframe_options_exempt
@csrf_exempt
def report_deals(request):
    """Метод Отчет по сделкам."""
    template: str = 'reports/report_deals.html'
    title: str = 'Отчеты'

    def _get_prodtime_values_from_report(prodtime_db):
        """Метод формирования значений товарной позиции со сроком
        производства для отчета."""
        str_blank = 0

        direct_costs = (prodtime_db.direct_costs if prodtime_db.direct_costs
                        else str_blank)
        direct_costs_fact = (prodtime_db.direct_costs_fact if
                             prodtime_db.direct_costs_fact else 0)
        if type(direct_costs) == decimal.Decimal:
            direct_costs_div = round((direct_costs_fact - direct_costs) /
                                     direct_costs * 100, 2)
        else:
            direct_costs_div = str_blank
        if direct_costs_fact:
            direct_costs_sum = round((direct_costs_fact + direct_costs_fact * prodtime.tax / 100) * prodtime.quantity, 2)
        elif direct_costs:
            direct_costs_sum = round((direct_costs + direct_costs * prodtime.tax / 100) * prodtime.quantity, 2)
        else:
            direct_costs_sum = 0

        standard_hours = (prodtime_db.standard_hours if
                          prodtime_db.standard_hours else str_blank)
        standard_hours_fact = (prodtime_db.standard_hours if
                               prodtime_db.standard_hours_fact else 0)
        if type(standard_hours) == decimal.Decimal:
            standard_hours_div = round((standard_hours_fact - standard_hours) /
                                       standard_hours * 100, 2)
        else:
            standard_hours_div = str_blank

        materials = (prodtime_db.materials if prodtime_db.materials
                     else str_blank)
        materials_fact = (prodtime_db.materials if prodtime_db.materials_fact
                          else 0)
        if type(materials) == decimal.Decimal:
            materials_div = round((materials_fact - materials) / materials *
                                  100, 2)
        else:
            materials_div = str_blank

        income = prodtime_db.income if prodtime_db.income else str_blank

        sum_brutto = round(prodtime.price_brutto * prodtime.quantity, 2)
        sum_price = round(prodtime.price * prodtime.quantity, 2)
        equivalent = prodtime.equivalent
        sum_equivalent = prodtime.equivalent_count
        margin = round(sum_price - direct_costs_sum, 2)
        factory_number = prodtime_db.factory_number if prodtime_db.factory_number else ''
        try:
            effectiveness = round((sum_price - direct_costs_sum) / sum_price * 100, 2)
        except Exception:
            effectiveness = 0

        return {
            'direct_costs': direct_costs,
            'direct_costs_fact': direct_costs_fact,
            'direct_costs_div': direct_costs_div,
            'direct_costs_sum': direct_costs_sum,
            'standard_hours': standard_hours,
            'standard_hours_fact': standard_hours_fact,
            'standard_hours_div': standard_hours_div,
            'materials': materials,
            'materials_fact': materials_fact,
            'materials_div': materials_div,
            'sum_brutto': sum_brutto,
            'sum_price': sum_price,
            'equivalent': equivalent,
            'sum_equivalent': sum_equivalent,
            'margin': margin,
            'effectiveness': effectiveness,
            'income': income,
            'factory_number': factory_number
        }

    def _get_result_for_products(products_list):
        """Метод для подсчета итогов по таблице продуктов."""

        def _sum(product_list, column_name):
            """Сумма по столбцу."""
            values = [item.get(column_name) for item in product_list
                      if type(item.get(column_name)) == decimal.Decimal]
            if values:
                return round(sum(values), 2)
            else:
                return 0

        def _sum_count(product_list, column_name):
            """Сумма по столбцу c учетом количества."""
            values = [item.get(column_name) * item.get('quantity') for item in
                      product_list if type(item.get(column_name)) ==
                      decimal.Decimal]
            if values:
                return round(sum(values), 2)
            else:
                return 0

        def _avg(product_list, column_name):
            """Среднее по столбцу."""
            values = [item.get(column_name) for item in product_list
                      if type(item.get(column_name)) == decimal.Decimal]
            if values:
                return round(sum(values) / len(values), 2)
            else:
                return 0

        def _custom_avg(value_one, value_two):
            """Среднее между двумя значениями."""
            if value_one:
                return round((value_two - value_one) / value_one * 100, 2)
            else:
                return 0

        res_equivalent = _sum(products_list, 'equivalent')
        res_quantity = sum([item.get('quantity') for item in products_list])
        res_direct_costs = _sum_count(products_list, 'direct_costs')
        res_direct_costs_fact = _sum_count(products_list, 'direct_costs_fact')
        res_direct_costs_div = _custom_avg(res_direct_costs,
                                           res_direct_costs_fact)
        res_standard_hours = _sum_count(products_list, 'standard_hours')
        res_standard_hours_fact = _sum_count(products_list,
                                             'standard_hours_fact')
        res_standard_hours_div = _custom_avg(res_standard_hours,
                                             res_standard_hours_fact)
        res_materials = _sum_count(products_list, 'materials')
        res_materials_fact = _sum_count(products_list, 'materials_fact')
        res_materials_div = _custom_avg(res_materials, res_materials_fact)
        res_sum_brutto = _sum(products_list, 'sum_brutto')
        res_sum_price = _sum(products_list, 'sum_price')
        res_sum_equivalent = _sum(products_list, 'sum_equivalent')
        res_direct_costs_sum = _sum(products_list, 'direct_costs_sum')
        res_margin = _sum(products_list, 'margin')
        res_effectiveness = _avg(products_list, 'effectiveness')
        res_income = _sum(products_list, 'income')

        return {
            'res_equivalent': res_equivalent,
            'res_quantity': res_quantity,
            'res_direct_costs': res_direct_costs,
            'res_direct_costs_fact': res_direct_costs_fact,
            'res_direct_costs_div': res_direct_costs_div,
            'res_standard_hours': res_standard_hours,
            'res_standard_hours_fact': res_standard_hours_fact,
            'res_standard_hours_div': res_standard_hours_div,
            'res_materials': res_materials,
            'res_materials_fact': res_materials_fact,
            'res_materials_div': res_materials_div,
            'res_sum_brutto': res_sum_brutto,
            'res_sum_price': res_sum_price,
            'res_sum_equivalent': res_sum_equivalent,
            'res_direct_costs_sum': res_direct_costs_sum,
            'res_margin': res_margin,
            'res_effectiveness': res_effectiveness,
            'res_income': res_income,
        }

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
    elif request.method == 'GET':
        member_id = request.GET.get('member_id')
    else:
        return render(request, 'error.html', {
            'error_name': 'QueryError',
            'error_description': 'Неизвестный тип запроса'
        })
    portal: Portals = create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)
    user_info = get_current_user(request, '', portal,
                                 settings_portal.is_admin_code)

    form = ReportDealsForm(request.POST or None)

    context = {
        'title': title,
        'member_id': member_id,
        'form': form,
        'user': user_info
    }
    if not form.is_valid():
        return render(request, template, context)

    start_date = request.POST.get('start_date') + "T00:00:00"
    end_date = request.POST.get('end_date') + "T23:59:59"
    filter_date = request.POST.get('date_code')
    stages_deals = request.POST.get('stages_deals')
    show_parent_dir = request.POST.get('show_parent_dir')
    filter_for_deal = {
        '0': {
            'logic': 'OR',
            '0': {
                '=categoryId': 4
            },
            '1': {
                '=categoryId': 5
            },
            '2': {
                '=categoryId': 6
            },
            '3': {
                '=categoryId': 8
            },
            '4': {
                '=categoryId': 11
            },
            '5': {
                '=categoryId': 16
            }
        },
        '1': {
            'logic': 'AND',
            '0': {
                '>=' + filter_date: start_date
            },
            '1': {
                '<=' + filter_date: end_date
            }
        }
    }
    if filter_date == 'ufCrm1652693659':
        filter_for_deal['ufCrm_1661330774842'] = 1
    if stages_deals != 'A':
        filter_for_deal['StageSemanticId'] = stages_deals
    deals = ListEntitiesB24(portal, filter_for_deal, 'item', ['id'])
    deals_ids = []
    for deal in deals.entities:
        deals_ids.append(deal.get('id'))
    filter_for_prods = {
        '=ownerType': 'D',
        '=ownerID': deals_ids
    }
    productrows = ListProductRowsB24(portal, filter_for_prods)
    if show_parent_dir == 'on':
        for count, productrow in enumerate(productrows.entities):
            if not productrow.get('productId') or int(
                    productrow.get('productId')) <= 0:
                continue
            try:
                product_in_catalog = ProductInCatalogB24(
                    portal, productrow.get('productId'))
                section_id = product_in_catalog.properties.get(
                    'iblockSectionId')
                section = CatalogSectionB24(portal, section_id)
                section_name = section.properties.get('section').get('name')
            except RuntimeError:
                continue
            productrows.entities[count]['section_name'] = section_name
    for count, productrow in enumerate(productrows.entities):
        try:
            prodtime = ProdTimeDeal.objects.get(
                portal=portal, product_id_b24=int(productrow.get('id')))
        except ObjectDoesNotExist:
            continue
        prodtime_values = _get_prodtime_values_from_report(prodtime)
        productrows.entities[count] = productrow | prodtime_values

    result_values = _get_result_for_products(productrows.entities)
    context = {
        'title': title,
        'member_id': member_id,
        'form': form,
        'user': user_info,
        'products': productrows.entities,
        'result': result_values,
        'show_parent_dir': show_parent_dir,
    }
    return render(request, template, context)


@xframe_options_exempt
@csrf_exempt
def report_production(request):
    """Метод отчета по производству."""
    template: str = 'reports/report_production.html'
    title: str = 'Отчеты'

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
    elif request.method == 'GET':
        member_id = request.GET.get('member_id')
    else:
        return render(request, 'error.html', {
            'error_name': 'QueryError',
            'error_description': 'Неизвестный тип запроса'
        })
    portal: Portals = create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)
    user_info = get_current_user(request, '', portal,
                                 settings_portal.is_admin_code)

    form = ReportProductionForm(request.POST or None)

    context = {
        'title': title,
        'member_id': member_id,
        'form': form,
        'user': user_info
    }
    if not form.is_valid():
        return render(request, template, context)

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    show_finish = form.cleaned_data['show_finish']
    show_made = form.cleaned_data['show_made']
    responsible = form.cleaned_data['responsible']

    prodtimes = ProdTimeDeal.objects.filter(prod_time__range=[start_date, end_date])
    if show_made:
        prodtimes = prodtimes.filter(made=show_made)
    if show_finish:
        prodtimes = prodtimes.filter(finish=show_finish)
    if responsible:
        deals_ids = Deal.objects.filter(responsible=responsible).values_list('deal_id', flat=True)
        prodtimes = prodtimes.filter(deal_id__in=deals_ids)

    deals = Deal.objects.all()
    invoices = {deal.deal_id: deal.invoice_number for deal in deals}
    responsibles = {deal.deal_id: deal.responsible.get_full_name() if deal.responsible else '' for deal in deals}

    results = {
        'quantity_sum': str(prodtimes.aggregate(Sum('quantity')).get('quantity__sum')),
        'sum_sum': str(prodtimes.aggregate(Sum('sum')).get('sum__sum')),
    }

    context = {
        'title': title,
        'member_id': member_id,
        'form': form,
        'user': user_info,
        'prodtimes': prodtimes,
        'results': results,
        'invoices': invoices,
        'responsibles': responsibles
    }
    return render(request, template, context)

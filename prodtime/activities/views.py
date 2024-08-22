import decimal
import core.methods as core_methods

from core.bitrix24.bitrix24 import ActivityB24, create_portal
from core.methods import calculation_income
from core.models import Portals
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from pybitrix24 import Bitrix24

from dealcard.models import ProdTimeDeal
from quotecard.models import ProdTimeQuote
from settings.models import SettingsPortal
from .models import Activity


@csrf_exempt
def install(request):
    """View-функция установки активити на портал."""
    member_id = request.POST.get('member_id')
    activity_code = request.POST.get('code')

    portal: Portals = create_portal(member_id)

    activity = get_object_or_404(Activity, code=activity_code)
    try:
        activity_b24 = ActivityB24(portal, obj_id=None)
        result = activity_b24.install(activity.build_params())
    except RuntimeError as ex:
        return JsonResponse({
            'result': 'False',
            'error_name': ex.args[0],
            'error_description': ex.args[1]})
    return JsonResponse({'result': result})


@csrf_exempt
def uninstall(request):
    """View-функция удаления активити на портале."""
    member_id = request.POST.get('member_id')
    activity_code = request.POST.get('code')

    portal: Portals = create_portal(member_id)

    try:
        activity_b24 = ActivityB24(portal, obj_id=None, code=activity_code)
        result = activity_b24.uninstall()
    except RuntimeError as ex:
        return JsonResponse({
            'result': 'False',
            'error_name': ex.args[0],
            'error_description': ex.args[1]})
    return JsonResponse({'result': result})


@csrf_exempt
def send_to_db(request):
    """View-функция для работы активити 'Передача значений полей в БД'."""
    initial_data = start_app(request)
    portal = create_portal(initial_data['member_id'])
    id_productrow, new_equivalent, new_materials, new_standard_hours, new_direct_costs, new_standard_hours_fact, \
    new_materials_fact, new_direct_costs_fact = check_initial_data(portal, initial_data)
    new_prodtime_str = initial_data['new_prodtime_str']

    prodtime = create_prodtime(portal, initial_data, id_productrow)

    if new_equivalent:
        prodtime.equivalent = new_equivalent
        prodtime.equivalent_count = prodtime.equivalent * prodtime.quantity
        prodtime.is_change_equivalent = True if initial_data['is_change_equivalent'] == 'Y' else False
    if new_prodtime_str:
        prodtime.prodtime_str = new_prodtime_str
        prodtime.is_change_prodtime_str = True if initial_data['is_change_prodtime_str'] == 'Y' else False
    if initial_data['document_type'] == 'DEAL':
        if new_materials:
            prodtime.materials = new_materials
            prodtime.is_change_materials = True if initial_data['is_change_materials'] == 'Y' else False
        if new_materials_fact:
            prodtime.materials_fact = new_materials_fact
        if new_standard_hours:
            prodtime.standard_hours = new_standard_hours
            prodtime.is_change_standard_hours = True if initial_data['is_change_standard_hours'] == 'Y' else False
        if new_standard_hours_fact:
            prodtime.standard_hours_fact = new_standard_hours_fact
        if new_direct_costs:
            prodtime.direct_costs = new_direct_costs
            prodtime.is_change_direct_costs = True if initial_data['is_change_direct_costs'] == 'Y' else False
        if new_direct_costs_fact:
            prodtime.direct_costs_fact = new_direct_costs_fact
    prodtime.save()

    create_response_for_bp(portal, initial_data, prodtime)
    return HttpResponse(status=200)


@csrf_exempt
def get_from_db(request):
    """View-функция для работы активити 'Получение значений полей в БД'."""
    if request.method != 'POST':
        return HttpResponse(status=200)
    initial_data = {
        'member_id': request.POST.get('auth[member_id]'),
        'event_token': request.POST.get('event_token'),
        'document_type': request.POST.get('document_type[2]'),
        'id_productrow': request.POST.get('properties[id_productrow]') or 0,
    }
    portal = create_portal(initial_data['member_id'])

    try:
        id_productrow = int(initial_data['id_productrow'])
    except Exception as ex:
        response_for_bp(
            portal,
            initial_data['event_token'], '{} {}'.format('Ошибка в начальных данных:', ex.args[0]),
            return_values={'result': 'Error', 'errors': 'Ошибка в начальных данных'}
        )
        return HttpResponse(status=200)

    prodtime = create_prodtime(portal, initial_data, id_productrow)
    create_response_for_bp(portal, initial_data, prodtime)

    return HttpResponse(status=200)


@csrf_exempt
def update_finish(request):
    """View-функция для работы активити 'Установить Готовность и Выпуск изделия'."""

    def _start_app(req):
        """Запуск приложения и проверка метода."""
        if req.method != 'POST':
            return HttpResponse(status=200)
        return {
            'member_id': req.POST.get('auth[member_id]'),
            'event_token': req.POST.get('event_token'),
            'document_type': req.POST.get('document_type[2]'),
            'object_id': req.POST.get('properties[object_id]') or 0,
            'finish': req.POST.get('properties[finish]'),
            'made': req.POST.get('properties[made]'),
        }

    def _check_initial_data(portal_obj, init_data):
        """Функция проверки начальных данных."""
        try:
            obj_id = int(init_data['object_id'])
            if init_data['finish']:
                fin = True if init_data['finish'] == 'Y' else False
            else:
                fin = 'not set'
            if init_data['made']:
                md = True if init_data['made'] == 'Y' else False
            else:
                md = 'not set'
            return obj_id, fin, md
        except Exception as ex:
            response_for_bp(
                portal_obj,
                init_data['event_token'], '{} {}'.format('Ошибка в начальных данных:', ex.args[0]),
                return_values={'result': 'Error', 'msg_error': 'Ошибка в начальных данных'}
            )
            return HttpResponse(status=200)

    def _create_response_for_bp(portal_obj, init_data):
        """Создать финальный ответ для БП."""
        response_for_bp(portal, init_data['event_token'], 'Активити успешно завершило свою работу',
                        return_values={
                            'result': 'Success', 'msg_success': 'Успешное обновление полей для товаров сделки'
                        })

    initial_data = _start_app(request)
    portal = create_portal(initial_data['member_id'])
    settings_portal = get_object_or_404(SettingsPortal, portal=portal)
    object_id, finish, made = _check_initial_data(portal, initial_data)

    if initial_data.get('document_type') != 'DEAL':
        response_for_bp(
            portal,
            initial_data['event_token'], 'Неизвестный тип сущности',
            return_values={'result': 'Error', 'msg_error': 'Активити работает только из сделки'}
        )
        return HttpResponse(status=200)

    prodtimes = ProdTimeDeal.objects.filter(portal=portal, deal_id=object_id)
    prodtimes_id = list(prodtimes.values_list('pk', flat=True))
    print(f'{prodtimes_id=}')

    if made != 'not set':
        prodtimes.update(made=made)
    if finish and finish != 'not set':
        general_msg = ''
        general_msg += f"Создание сделки:\n"
        result = core_methods.create_shipment_element(portal, settings_portal, object_id, prodtimes_id)
        try:
            new_deal_id = int(result.get('info'))
        except ValueError:
            new_deal_id = 0
        general_msg += str(result.get('info'))
        general_msg += f"\nСоздание элемента смарт процесса:\n"
        result = core_methods.create_shipment_element(portal, settings_portal, object_id, prodtimes_id,
                                                      type_elem='smart')
        general_msg += str(result.get('info'))
        general_msg += f"\nСоздание задачи:\n"
        result = core_methods.create_shipment_task(portal, settings_portal, new_deal_id)
        general_msg += str(result.get('info'))
        core_methods.save_finish(prodtimes_id)
        # result = core_methods.create_shipment_element(portal, settings_portal, object_id, prodtimes_id)
        # if result.get('result') == 'msg':
        #     response_for_bp(portal, initial_data['event_token'], 'Информация',
        #                     return_values={'result': 'Error', 'msg_error': result.get('info')})
        #     return HttpResponse(status=200)
        # deal_bx = result.get('info')
        # result = core_methods.create_shipment_task(portal, settings_portal, deal_bx)
        response_for_bp(portal, initial_data['event_token'], 'Активити успешно завершило свою работу',
                        return_values={'result': 'Success', 'msg_success':
                        f'Успешное обновление полей для товаров сделки.\n{general_msg}'})
        return HttpResponse(status=200)
    elif not finish:
        prodtimes.update(finish=finish)

    _create_response_for_bp(portal, initial_data)
    return HttpResponse(status=200)


@csrf_exempt
def update_income(request):
    """View-функция для работы активити 'Пересчет плановой прибыли'."""

    def _start_app(req):
        """Запуск приложения и проверка метода."""
        if req.method != 'POST':
            return HttpResponse(status=200)
        return {
            'member_id': req.POST.get('auth[member_id]'),
            'event_token': req.POST.get('event_token'),
            'document_type': req.POST.get('document_type[2]'),
            'object_id': req.POST.get('properties[object_id]') or 0,
        }

    def _check_initial_data(portal_obj, init_data):
        """Функция проверки начальных данных."""
        try:
            obj_id = int(init_data['object_id'])
            return obj_id
        except Exception as ex:
            response_for_bp(
                portal_obj,
                init_data['event_token'], '{} {}'.format('Ошибка в начальных данных:', ex.args[0]),
                return_values={'result': 'Error', 'msg_error': 'Ошибка в начальных данных'}
            )
            return HttpResponse(status=200)

    def _create_response_for_bp(portal_obj, init_data):
        """Создать финальный ответ для БП."""
        response_for_bp(portal, init_data['event_token'], 'Активити успешно завершило свою работу',
                        return_values={
                            'result': 'Success', 'msg_success': 'Пересчет плановой прибыли выполнен'
                        })

    initial_data = _start_app(request)
    portal = create_portal(initial_data['member_id'])
    object_id = _check_initial_data(portal, initial_data)

    if initial_data.get('document_type') == 'DEAL':
        prodtimes = ProdTimeDeal.objects.filter(portal=portal, deal_id=object_id)
    elif initial_data.get('document_type') == 'QUOTE':
        prodtimes = ProdTimeQuote.objects.filter(portal=portal, quote_id=object_id)
    else:
        response_for_bp(
            portal,
            initial_data['event_token'], 'Неизвестный тип сущности',
            return_values={'result': 'Error', 'msg_error': 'Активити работает только из сделки или предложения'}
        )
        return HttpResponse(status=200)

    settings_portal = get_object_or_404(SettingsPortal, portal=portal)
    calculation_income(prodtimes, settings_portal)
    _create_response_for_bp(portal, initial_data)
    return HttpResponse(status=200)


def create_prodtime(portal, initial_data, id_productrow):
    """Создать модели."""
    try:
        if initial_data['document_type'] == 'DEAL':
            prodtime = ProdTimeDeal.objects.get(portal=portal, product_id_b24=id_productrow)
        elif initial_data['document_type'] == 'QUOTE':
            prodtime = ProdTimeQuote.objects.get(portal=portal, product_id_b24=id_productrow)
        else:
            response_for_bp(portal, initial_data['event_token'], 'Ошибки в работе активити',
                            return_values={'result': 'Error', 'errors': 'Активити запущено из неизвестного документа. '
                                                                        'Запуск возможен только с Предложения или '
                                                                        'Сделки.'})
            return HttpResponse(status=200)
    except ProdTimeDeal.DoesNotExist:
        response_for_bp(portal, initial_data['event_token'], 'Ошибки в работе активити',
                        return_values={'result': 'Error', 'errors': f'Товарная позиция с id {id_productrow} не '
                                                                    'найдена в базе данных приложения'})
        return HttpResponse(status=200)
    return prodtime


def create_response_for_bp(portal, initial_data, prodtime):
    """Создать финальный ответ для БП."""
    if initial_data['document_type'] == 'DEAL':
        response_for_bp(portal, initial_data['event_token'], 'Активити успешно завершило свою работу',
                        return_values={
                            'result': 'Success',
                            'equivalent_value': str(prodtime.equivalent),
                            'materials_value': str(prodtime.materials),
                            'standard_hours_value': str(prodtime.standard_hours),
                            'direct_costs_value': str(prodtime.direct_costs),
                            'materials_fact_value': str(prodtime.materials_fact),
                            'standard_hours_fact_value': str(prodtime.standard_hours_fact),
                            'direct_costs_fact_value': str(prodtime.direct_costs_fact),
                            'prodtime_str_value': prodtime.prodtime_str,
                        })
    elif initial_data['document_type'] == 'QUOTE':
        response_for_bp(portal, initial_data['event_token'], 'Активити успешно завершило свою работу',
                        return_values={
                            'result': 'Success',
                            'equivalent_value': str(prodtime.equivalent),
                            'prodtime_str_value': prodtime.prodtime_str,
                        })


def response_for_bp(portal, event_token, log_message, return_values=None):
    """Метод отправки параметров ответа в БП."""
    bx24 = Bitrix24(portal.name)
    bx24._access_token = portal.auth_id
    method_rest = 'bizproc.event.send'
    params = {
        'event_token': event_token,
        'log_message': log_message,
        'return_values': return_values,
    }
    bx24.call(method_rest, params)


def start_app(request):
    """Запуск приложения и проверка метода."""
    if request.method != 'POST':
        return HttpResponse(status=200)
    return {
        'member_id': request.POST.get('auth[member_id]'),
        'event_token': request.POST.get('event_token'),
        'document_type': request.POST.get('document_type[2]'),
        'id_productrow': request.POST.get('properties[id_productrow]') or 0,
        'new_equivalent': request.POST.get('properties[new_equivalent]') or 0,
        'is_change_equivalent': request.POST.get('properties[is_change_equivalent]'),
        'new_materials': request.POST.get('properties[new_materials]') or 0,
        'is_change_materials': request.POST.get('properties[is_change_materials]'),
        'new_standard_hours': request.POST.get('properties[new_standard_hours]') or 0,
        'is_change_standard_hours': request.POST.get('properties[is_change_standard_hours]'),
        'new_prodtime_str': request.POST.get('properties[new_prodtime_str]'),
        'is_change_prodtime_str': request.POST.get('properties[is_change_prodtime_str]'),
        'new_direct_costs': request.POST.get('properties[new_direct_costs]') or 0,
        'is_change_direct_costs': request.POST.get('properties[is_change_direct_costs]'),
        'new_materials_fact': request.POST.get('properties[new_materials_fact]') or 0,
        'new_standard_hours_fact': request.POST.get('properties[new_standard_hours_fact]') or 0,
        'new_direct_costs_fact': request.POST.get('properties[new_direct_costs_fact]') or 0,
    }


def check_initial_data(portal, initial_data):
    """Функция проверки начальных данных."""
    try:
        id_productrow = int(initial_data['id_productrow'])
        new_materials = decimal.Decimal(initial_data['new_materials'])
        new_standard_hours = decimal.Decimal(initial_data['new_standard_hours'])
        new_direct_costs = decimal.Decimal(initial_data['new_direct_costs'])
        new_equivalent = decimal.Decimal(initial_data['new_equivalent'])
        new_standard_hours_fact = decimal.Decimal(initial_data['new_standard_hours_fact'])
        new_materials_fact = decimal.Decimal(initial_data['new_materials_fact'])
        new_direct_costs_fact = decimal.Decimal(initial_data['new_direct_costs_fact'])
        return id_productrow, new_equivalent, new_materials, new_standard_hours, new_direct_costs, \
               new_standard_hours_fact, new_materials_fact, new_direct_costs_fact
    except Exception as ex:
        response_for_bp(
            portal,
            initial_data['event_token'], '{} {}'.format('Ошибка в начальных данных:', ex.args[0]),
            return_values={'result': 'Error', 'errors': 'Ошибка в начальных данных'}
        )
        return HttpResponse(status=200)

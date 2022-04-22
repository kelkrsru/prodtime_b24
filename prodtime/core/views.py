from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from pybitrix24 import Bitrix24

from .models import Portals
from settings.models import SettingsPortal


@xframe_options_exempt
@csrf_exempt
def install(request):
    """Метод установки приложения"""

    params: dict[str, str] = {
        'PLACEMENT': 'CRM_DEAL_DETAIL_TAB',
        'HANDLER': 'https://devkel.ru/dealcard/', ##########
        'TITLE': 'Срок производства',
        'DESCRIPTION': 'Приложение для указания сроков производства товаров'
    }

    try:
        portal: Portals = Portals.objects.get(
            member_id=request.POST['member_id'])
        portal.auth_id = request.POST['AUTH_ID']
        portal.refresh_id = request.POST['REFRESH_ID']
        portal.save()
    except Portals.DoesNotExist:
        portal: Portals = Portals.objects.create(
            member_id=request.POST['member_id'],
            name=request.GET.get('DOMAIN'),
            auth_id=request.POST['AUTH_ID'],
            refresh_id=request.POST['REFRESH_ID']
        )
    try:
        SettingsPortal.objects.get(portal=portal)
    except SettingsPortal.DoesNotExist:
        SettingsPortal.objects.create(portal=portal)

    bx24 = Bitrix24(portal.name)
    bx24._access_token = portal.auth_id
    bx24._refresh_token = portal.refresh_id

    result = bx24.call('placement.bind', params)
    if 'error' in result:
        return render(request, 'error.html', {
            'error_name': result['error'],
            'error_description': result['error_description'],
        })

    return render(request, 'core/install.html')

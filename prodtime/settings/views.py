from django.shortcuts import render, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from typing import Optional

from core.bitrix24.bitrix24 import create_portal
from .models import SettingsPortal
from .forms import (SettingsDealPortalForm, SettingsEquivalentPortalForm,
                    SettingsFactoryNumbersPortalForm,
                    SettingsArticlesPortalForm, SettingsGeneralPortalForm)
from core.models import TemplateDocFields, Portals


@xframe_options_exempt
@csrf_exempt
def index(request):

    template: Optional[str] = 'settings/index.html'
    active_tab = 1

    if request.method == 'POST':
        member_id: Optional[str] = request.POST.get('member_id')
    elif request.method == 'GET':
        member_id: Optional[str] = request.GET.get('member_id')
    else:
        return render(request, 'error.html', {
            'error_name': 'QueryError',
            'error_description': 'Неизвестный тип запроса'
        })

    portal: Portals = create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    if 'save-settings-deal' in request.POST:
        form_deal: SettingsDealPortalForm = SettingsDealPortalForm(
            request.POST or None,
            instance=settings_portal,
        )
        if form_deal.is_valid():
            fields_form = form_deal.save(commit=False)
            fields_form.portal = portal
            fields_form.save()
    else:
        form_deal: SettingsDealPortalForm = SettingsDealPortalForm(
            instance=settings_portal,
        )

    if 'save-settings-equivalent' in request.POST:
        form_equ: SettingsEquivalentPortalForm = SettingsEquivalentPortalForm(
            request.POST or None,
            instance=settings_portal,
        )
        if form_equ.is_valid():
            fields_form = form_equ.save(commit=False)
            fields_form.portal = portal
            fields_form.save()
        active_tab = 2
    else:
        form_equ: SettingsEquivalentPortalForm = SettingsEquivalentPortalForm(
            instance=settings_portal,
        )

    if 'save-settings-factory_numbers' in request.POST:
        form_fn = SettingsFactoryNumbersPortalForm(
            request.POST or None,
            instance=settings_portal,
        )
        if form_fn.is_valid():
            fields_form = form_fn.save(commit=False)
            fields_form.portal = portal
            fields_form.save()
        active_tab = 3
    else:
        form_fn = SettingsFactoryNumbersPortalForm(instance=settings_portal)

    if 'save-settings-article' in request.POST:
        form_art = SettingsArticlesPortalForm(
            request.POST or None,
            instance=settings_portal,
        )
        if form_art.is_valid():
            fields_form = form_art.save(commit=False)
            fields_form.portal = portal
            fields_form.save()
        active_tab = 4
    else:
        form_art = SettingsArticlesPortalForm(instance=settings_portal)

    if 'save-settings-general' in request.POST:
        form_general = SettingsGeneralPortalForm(
            request.POST or None,
            instance=settings_portal,
        )
        if form_general.is_valid():
            fields_form = form_art.save(commit=False)
            fields_form.portal = portal
            fields_form.save()
        active_tab = 5
    else:
        form_general = SettingsGeneralPortalForm(instance=settings_portal)

    fields = TemplateDocFields.objects.all()
    context = {
        'fields': fields,
        'form_deal': form_deal,
        'form_equ': form_equ,
        'form_fn': form_fn,
        'form_art': form_art,
        'form_general': form_general,
        'member_id': member_id,
        'active_tab': active_tab,
    }
    return render(request, template, context)

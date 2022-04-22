from django.shortcuts import render, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from typing import Optional

from .models import SettingsPortal
from .forms import SettingsPortalForm
from core.models import TemplateDocFields, Portals
from dealcard.views import _create_portal


@xframe_options_exempt
@csrf_exempt
def index(request):

    template: Optional[str] = 'settings/index.html'

    if request.method == 'POST':
        member_id: Optional[str] = request.POST.get('member_id')
    elif request.method == 'GET':
        member_id: Optional[str] = request.GET.get('member_id')
    else:
        return render(request, 'error.html', {
            'error_name': 'QueryError',
            'error_description': 'Неизвестный тип запроса'
        })

    portal: Portals = _create_portal(member_id)
    settings_portal: SettingsPortal = get_object_or_404(SettingsPortal,
                                                        portal=portal)

    if 'save-settings' in request.POST:
        form: SettingsPortalForm = SettingsPortalForm(
            request.POST or None,
            instance=settings_portal,
        )
        if form.is_valid():
            fields_form = form.save(commit=False)
            fields_form.portal = portal
            fields_form.save()
    else:
        form: SettingsPortalForm = SettingsPortalForm(
            instance=settings_portal,
        )

    fields = TemplateDocFields.objects.all()
    context = {
        'fields': fields,
        'form': form,
        'member_id': member_id,
    }
    return render(request, template, context)

from django import forms

from .models import SettingsPortal


class SettingsPortalForm(forms.ModelForm):
    """Форма Настройки портала"""

    class Meta:
        model = SettingsPortal
        fields = ('create_deal', 'name_deal', 'create_task', 'name_task',
                  'task_deadline',)

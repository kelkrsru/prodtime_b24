from django import forms

from .models import SettingsPortal


class SettingsDealPortalForm(forms.ModelForm):
    """Форма Настройки портала"""

    class Meta:
        model = SettingsPortal
        fields = ('create_deal', 'name_deal', 'category_id', 'stage_code',
                  'real_deal_code', 'create_task', 'name_task',
                  'task_deadline',)


class SettingsEquivalentPortalForm(forms.ModelForm):
    """Форма Настройки портала"""

    class Meta:
        model = SettingsPortal
        fields = ('section_list_id', 'default_section_id', 'real_section_code',
                  'copy_section_code', 'equivalent_code',
                  'sum_equivalent_code',)

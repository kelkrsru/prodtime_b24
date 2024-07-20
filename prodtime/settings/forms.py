from django import forms

from .models import SettingsPortal


class SettingsDealPortalForm(forms.ModelForm):
    """Форма Настройки портала для создания сделки и задачи."""

    class Meta:
        model = SettingsPortal
        fields = ('create_deal', 'name_deal', 'category_id', 'stage_code', 'real_deal_code', 'sum_direct_costs_code',
                  'sum_direct_costs_fact_code' ,'create_task', 'name_task', 'task_deadline',)


class SettingsEquivalentPortalForm(forms.ModelForm):
    """Форма Настройки портала для нумерации КП и эквивалента."""

    class Meta:
        model = SettingsPortal
        fields = ('section_list_id', 'default_section_id', 'real_section_code',
                  'copy_section_code', 'equivalent_code',
                  'sum_equivalent_code', 'template_id', 'kp_code',
                  'kp_last_num_code')


class SettingsFactoryNumbersPortalForm(forms.ModelForm):
    """Форма Настройки портала копирования в каталог и заводских номеров."""

    class Meta:
        model = SettingsPortal
        fields = ('smart_factory_number_id', 'smart_factory_number_short_code',
                  'smart_factory_number_code', 'factory_number_code',
                  'responsible_id_copy_catalog', 'price_with_tax_code')


class SettingsArticlesPortalForm(forms.ModelForm):
    """Форма Настройки портала присваивания артикулов и прямых затрат"""

    class Meta:
        model = SettingsPortal
        fields = ('is_auto_article_code', 'article_code',
                  'section_number_code', 'service_code', 'prodtime_str_code',
                  'direct_costs_code', 'standard_hours_code',
                  'materials_code', 'income_percent', 'deal_field_code_income_res')


class SettingsGeneralPortalForm(forms.ModelForm):
    """Форма Настройки портала основных настроек и прав доступа"""

    class Meta:
        model = SettingsPortal
        fields = ('is_admin_code', 'max_prodtime_code',)

from django import forms

from .models import SettingsPortal, SettingsForReportStock


class SettingsForReportStockForm(forms.ModelForm):
    """Форма Настроек отчета по Остаткам."""

    class Meta:
        model = SettingsForReportStock
        fields = ('stock_id', 'min_stock_code', 'max_stock_code', 'considered_paid_stages', 'create_task', 'name_task',
                  'text_task', 'task_deadline', 'task_project_id', 'task_responsible_code',
                  'task_responsible_default_id', 'task_responsible_default_always', 'task_id_code',
                  'create_task_average', 'name_task_average', 'text_task_average', 'task_average_deadline',
                  'task_average_project_id', 'task_average_responsible_code', 'task_average_responsible_default_id',
                  'task_average_responsible_default_always', 'task_average_id_code', 'background_row',
                  'background_row_max', 'background_row_average')


class SettingsDealPortalForm(forms.ModelForm):
    """Форма Настройки портала для создания сделки и задачи."""

    class Meta:
        model = SettingsPortal
        fields = ('create_deal', 'name_deal', 'category_id', 'stage_code', 'real_deal_code', 'sum_direct_costs_code',
                  'sum_direct_costs_fact_code', 'create_smart',  'id_smart', 'code_smart', 'stage_smart', 'name_smart',
                  'sum_equivalent_code_smart', 'real_deal_code_smart', 'sum_direct_costs_code_smart',
                  'sum_direct_costs_fact_code_smart', 'max_prodtime_smart', 'create_task', 'name_task',
                  'task_deadline',)


class SettingsEquivalentPortalForm(forms.ModelForm):
    """Форма Настройки портала для нумерации КП и эквивалента."""

    class Meta:
        model = SettingsPortal
        fields = ('section_list_id', 'default_section_id', 'real_section_code',
                  'copy_section_code', 'equivalent_code',
                  'sum_equivalent_code', 'sum_equivalent_quote_code', 'template_id', 'kp_code',
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
        fields = ('is_auto_article_code', 'article_code', 'section_number_code', 'service_code', 'prodtime_str_code',
                  'direct_costs_code', 'standard_hours_code',  'standard_hours2_code', 'standard_hours3_code',
                  'standard_hours4_code', 'plot_number_code', 'materials_code', 'income_percent',
                  'deal_field_code_income_res')


class SettingsGeneralPortalForm(forms.ModelForm):
    """Форма Настройки портала основных настроек и прав доступа"""

    class Meta:
        model = SettingsPortal
        fields = ('is_admin_code', 'max_prodtime_code', 'num_invoice_code', 'token')

from django.db import models

from core.models import ProdTime, Entity, Responsible


class ProdTimeDeal(ProdTime):
    """Модель товара со сроком производства в сделке."""

    deal_id = models.IntegerField(
        verbose_name='ID сделки Битрикс24',
    )
    direct_costs = models.DecimalField(
        verbose_name='Прямые затраты',
        help_text='Прямые затраты из свойства товара в каталоге товаров '
                  'Битрикс24',
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )
    is_change_direct_costs = models.BooleanField(
        verbose_name='Ручное изменение прямых затрат',
        default=False
    )
    direct_costs_fact = models.DecimalField(
        verbose_name='Прямые затраты Факт',
        help_text='Фактические Прямые затраты. Указываются в приложении',
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )
    standard_hours = models.DecimalField('НЧ Уч.1', help_text='НЧ Уч.1 из свойства товара в каталоге товаров Битрикс24',
                                         max_digits=12, decimal_places=3, null=True, blank=True, )
    is_change_standard_hours = models.BooleanField('Ручное изменение НЧ Уч.1', default=False)
    standard_hours_fact = models.DecimalField('НЧ Уч.1 Факт', help_text='Фактические НЧ Уч.1. Указываются в приложении',
                                              max_digits=12, decimal_places=3, null=True, blank=True, )
    standard_hours2 = models.DecimalField('НЧ Уч.2',
                                          help_text='НЧ Уч.2 из свойства товара в каталоге товаров Битрикс24',
                                          max_digits=12, decimal_places=3, null=True, blank=True, )
    is_change_standard_hours2 = models.BooleanField('Ручное изменение НЧ Уч.2', default=False)
    standard_hours2_fact = models.DecimalField('НЧ Уч.2 Факт',
                                               help_text='Фактические НЧ Уч.2. Указываются в приложении',
                                               max_digits=12, decimal_places=3, null=True, blank=True, )
    standard_hours3 = models.DecimalField('НЧ Уч.3',
                                          help_text='НЧ Уч.3 из свойства товара в каталоге товаров Битрикс24',
                                          max_digits=12, decimal_places=3, null=True, blank=True, )
    is_change_standard_hours3 = models.BooleanField('Ручное изменение НЧ Уч.3', default=False)
    standard_hours3_fact = models.DecimalField('НЧ Уч.3 Факт',
                                               help_text='Фактические НЧ Уч.3. Указываются в приложении',
                                               max_digits=12, decimal_places=3, null=True, blank=True, )
    standard_hours4 = models.DecimalField('НЧ Уч.4',
                                          help_text='НЧ Уч.4 из свойства товара в каталоге товаров Битрикс24',
                                          max_digits=12, decimal_places=3, null=True, blank=True, )
    is_change_standard_hours4 = models.BooleanField('Ручное изменение НЧ Уч.4', default=False)
    standard_hours4_fact = models.DecimalField('НЧ Уч.4 Факт',
                                               help_text='Фактические НЧ Уч.4. Указываются в приложении',
                                               max_digits=12, decimal_places=3, null=True, blank=True, )
    materials = models.DecimalField(
        verbose_name='Материалы',
        help_text='Материалы из свойства товара в каталоге товаров Битрикс24',
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )
    is_change_materials = models.BooleanField(
        verbose_name='Ручное изменение материалов',
        default=False
    )
    materials_fact = models.DecimalField(
        verbose_name='Материалы Факт',
        help_text='Фактические Материалы. Указываются в приложении',
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )
    prodtime_str = models.CharField(
        verbose_name='Срок производства',
        help_text='Произвольное указание срока производства',
        max_length=1024,
        null=True,
        blank=True,
    )
    is_change_prodtime_str = models.BooleanField(
        verbose_name='Ручное изменение Срока производства',
        default=False,
    )

    class Meta:
        verbose_name = 'Срок производства в сделке'
        verbose_name_plural = 'Сроки производства в сделке'
        ordering = ['portal', 'deal_id', 'pk']
        unique_together = ['product_id_b24', 'portal']
        indexes = [models.Index(fields=['product_id_b24', 'portal'], name='prod_id_b24_portal_index')]


class Deal(Entity):
    """Модель для хранения параметров Сделки."""

    deal_id = models.IntegerField(
        verbose_name='ID сделки Битрикс24',
    )
    responsible = models.ForeignKey(
        Responsible,
        on_delete=models.PROTECT,
        verbose_name='Ответственный',
        null=True,
        blank=True,
    )
    invoice_number = models.CharField(
        max_length=255,
        verbose_name='Номер счета',
        help_text='Номер счета из пользовательского поля сделки',
        null=True,
        blank=True,
    )
    max_prodtime = models.DateField('Максимальный срок производства', null=True, blank=True)

    class Meta:
        verbose_name = 'Параметры сделки'
        verbose_name_plural = 'Параметры сделки'
        ordering = ['portal', 'deal_id']
        unique_together = ['portal', 'deal_id']

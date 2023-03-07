from django.db import models

from core.models import ProdTime, Entity


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
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_change_direct_costs = models.BooleanField(
        verbose_name='Ручное изменение прямых затрат',
        default=False
    )
    standard_hours = models.DecimalField(
        verbose_name='Нормочасы',
        help_text='Нормочасы из свойства товара в каталоге товаров Битрикс24',
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_change_standard_hours = models.BooleanField(
        verbose_name='Ручное изменение нормочасов',
        default=False
    )
    materials = models.DecimalField(
        verbose_name='Материалы',
        help_text='Материалы из свойства товара в каталоге товаров Битрикс24',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_change_materials = models.BooleanField(
        verbose_name='Ручное изменение материалов',
        default=False
    )

    class Meta:
        verbose_name = 'Срок производства в сделке'
        verbose_name_plural = 'Сроки производства в сделке'
        ordering = ['portal', 'deal_id', 'pk']


class Deal(Entity):
    """Модель для хранения параметров Сделки."""

    deal_id = models.IntegerField(
        verbose_name='ID сделки Битрикс24',
    )

    class Meta:
        verbose_name = 'Параметры сделки'
        verbose_name_plural = 'Параметры сделки'
        ordering = ['portal', 'deal_id']
        unique_together = ['portal', 'deal_id']

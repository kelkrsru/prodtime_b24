from django.db import models

from core.models import ProdTime, Entity


class ProdTimeDeal(ProdTime):
    """Модель товара со сроком производства в сделке."""

    deal_id = models.IntegerField(
        verbose_name='ID сделки Битрикс24',
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

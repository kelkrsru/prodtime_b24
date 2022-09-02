from django.db import models

from core.models import Portals, ProdTime


class ProdTimeQuote(ProdTime):
    """Модель товара со сроком производства в предложении."""

    quote_id = models.IntegerField(
        verbose_name='ID предложения Битрикс24',
    )

    class Meta:
        verbose_name = 'Срок производства в предложении'
        verbose_name_plural = 'Сроки производства в предложении'
        ordering = ['portal', 'quote_id', 'pk']

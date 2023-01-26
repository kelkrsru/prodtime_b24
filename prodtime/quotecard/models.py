from django.db import models

from core.models import Portals, ProdTime


class ProdTimeQuote(ProdTime):
    """Модель товара со сроком производства в предложении."""

    quote_id = models.IntegerField(
        verbose_name='ID предложения Битрикс24',
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
        verbose_name = 'Срок производства в предложении'
        verbose_name_plural = 'Сроки производства в предложении'
        ordering = ['portal', 'quote_id', 'pk']

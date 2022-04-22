from django.db import models

from core.models import Portals


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания и дату обновления"""

    created = models.DateField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )
    updated = models.DateField(
        verbose_name='Дата изменения',
        auto_now=True,
    )

    class Meta:
        abstract = True


class ProdTime(CreatedModel):
    """Модель товара со сроком производства"""

    product_id_b24 = models.IntegerField(
        verbose_name='ID товарной позиции в сделке Битрикс24',
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255,
    )
    name_for_print = models.CharField(
        verbose_name='Наименование в печатную форму',
        max_length=255,
    )
    price = models.DecimalField(
        verbose_name='Цена со скидкой и налогом',
        help_text='Цена за единицу товарной позиции с учетом скидок и налогов',
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    price_account = models.DecimalField(
        verbose_name='Цена со скидкой и налогом в валюте отчетов',
        help_text='Цена за единицу товарной позиции с учетом скидок и налогов,'
                  ' сконвертированная в валюту отчетов',
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    price_exclusive = models.DecimalField(
        verbose_name='Цена со скидкой, без налога',
        help_text='Цена за единицу товарной позиции с учетом скидок, но без '
                  'учета налогов',
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    price_netto = models.DecimalField(
        verbose_name='Цена без скидки, без налога',
        help_text='Цена за единицу товарной позиции без учета скидок и без '
                  'учета налогов',
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    price_brutto = models.DecimalField(
        verbose_name='Цена с налогом, без скидки',
        help_text='Цена за единицу товарной позиции с учетом налогов, но без '
                  'учета скидок',
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    quantity = models.DecimalField(
        verbose_name='Количество',
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    measure_code = models.IntegerField(
        verbose_name='Код единицы измерения',
    )
    measure_name = models.CharField(
        verbose_name='Единица измерения',
        max_length=10,
    )
    bonus_type_id = models.IntegerField(
        verbose_name='Тип скидки',
        help_text='Может быть 1 для скидки в абсолютном значении и 2 для '
                  'скидки в процентах. По умолчанию равно 2'
    )
    bonus = models.DecimalField(
        verbose_name='Процент скидки',
        max_digits=5,
        decimal_places=2,
        null=True,
    )
    bonus_sum = models.DecimalField(
        verbose_name='Сумма скидки',
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    tax = models.DecimalField(
        verbose_name='Процент налога',
        max_digits=5,
        decimal_places=2,
        null=True,
    )
    tax_included = models.BooleanField(
        verbose_name='Налог включен в цену',
        default=False,
    )
    tax_sum = models.DecimalField(
        verbose_name='Сумма налога',
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    sum = models.DecimalField(
        verbose_name='Сумма',
        max_digits=12,
        decimal_places=2,
        null=True,
    )
    prod_time = models.DateField(
        verbose_name='Срок производства',
        null=True,
        blank=True,
    )
    count_days = models.DecimalField(
        verbose_name='Количество рабочих дней',
        max_digits=12,
        decimal_places=1,
        null=True,
        blank=True,
    )
    finish = models.BooleanField(
        verbose_name='Готовность изделия',
        default=False,
    )
    deal_id = models.IntegerField(
        verbose_name='ID сделки Битрикс24',
    )
    portal = models.ForeignKey(
        Portals,
        verbose_name='Портал',
        related_name='prodtimes',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Срок производства'
        verbose_name_plural = 'Сроки производства'
        unique_together = ['product_id_b24', 'portal']
        ordering = ['portal', 'deal_id', 'pk']

    def __str__(self):
        return self.name

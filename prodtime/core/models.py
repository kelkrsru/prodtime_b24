from django.db import models


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


class Portals(models.Model):
    """Модель портала Битрикс24"""
    member_id = models.CharField(
        verbose_name='Уникальный код портала',
        max_length=255,
        unique=True,
    )
    name = models.CharField(
        verbose_name='Имя портала',
        max_length=255,
    )
    auth_id = models.CharField(
        verbose_name='Токен аутентификации',
        max_length=255,
    )
    auth_id_create_date = models.DateTimeField(
        verbose_name='Дата получения токена аутентификации',
        auto_now=True,
    )
    refresh_id = models.CharField(
        verbose_name='Токен обновления',
        max_length=255,
    )
    client_id = models.CharField(
        verbose_name='Уникальный ID клиента',
        max_length=50,
        null=True,
        blank=True,
    )
    client_secret = models.CharField(
        verbose_name='Секретный токен клиента',
        max_length=100,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Портал'
        verbose_name_plural = 'Порталы'

    def __str__(self):
        return self.name


class TemplateDocFields(models.Model):
    """Модель полей документа для вставки в шаблон"""
    name = models.CharField(
        verbose_name='Наименование',
        help_text='Понятное наименование',
        max_length=255,
    )
    code_b24 = models.CharField(
        verbose_name='Код из Битрикс24',
        help_text='Код из стандартного генератора шаблонов Битрикс24',
        max_length=50,
    )
    code = models.CharField(
        verbose_name='Код в приложении',
        help_text='Код для вставки шаблон для использования полей приложения',
        max_length=50,
    )
    code_db = models.CharField(
        verbose_name='Код в базе данных',
        help_text='Код поля в базе данных приложения для сопоставления',
        max_length=50,
        default='code_db',
    )

    class Meta:
        verbose_name = 'Поле документа шаблона'
        verbose_name_plural = 'Поля документа шаблона'

    def __str__(self):
        return self.name


class ProdTime(CreatedModel):
    """Модель товара со сроком производства."""

    product_id_b24 = models.IntegerField(
        verbose_name='ID товарной позиции',
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=1024,
    )
    name_for_print = models.CharField(
        verbose_name='Наименование в печатную форму',
        max_length=1024,
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
    equivalent = models.DecimalField(
        verbose_name='Эквивалент',
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )
    equivalent_count = models.DecimalField(
        verbose_name='Эквивалент с учетом количества',
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )
    is_change_equivalent = models.BooleanField(
        verbose_name='Ручное изменение эквивалента',
        default=False,
    )
    finish = models.BooleanField(
        verbose_name='Выпуск изделия',
        default=False,
    )
    made = models.BooleanField(
        verbose_name='Готовность изделия',
        default=False,
    )
    sort = models.PositiveIntegerField(
        verbose_name='Сортировка',
        default=0
    )
    portal = models.ForeignKey(
        Portals,
        verbose_name='Портал',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        unique_together = ['product_id_b24', 'portal']

from django.db import models


class Activity(models.Model):
    """Модель Активити."""
    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,
    )
    code = models.CharField(
        verbose_name='Код',
        max_length=50,
    )
    description = models.CharField(
        verbose_name='Описание',
        max_length=256,
    )
    handler = models.URLField(
        verbose_name='URL обработчика',
    )
    auth_user_id = models.IntegerField(
        verbose_name='ID пользователя Битрикс24',
        default=1
    )
    use_subscription = models.BooleanField(
        verbose_name='Ожидать ответа',
        default=False,
    )
    fields = models.ManyToManyField(
        'FieldsActivity',
        verbose_name='Поля',
        related_name='activities'
    )
    is_active = models.BooleanField(
        verbose_name='Активность',
        default=True,
    )

    class Meta:
        verbose_name = 'Активити'
        verbose_name_plural = 'Активити'

    def __str__(self):
        return self.code

    def build_params(self):
        return {
            'CODE': self.code,
            'HANDLER': self.handler,
            'AUTH_USER_ID': self.auth_user_id,
            'USE_SUBSCRIPTION': 'Y' if self.use_subscription else 'N',
            'NAME': self.name,
            'DESCRIPTION': self.description,
            'PROPERTIES': {
                prop.code: {
                    'Name': prop.name,
                    'Type': prop.type,
                    'Required': 'Y' if prop.required else 'N',
                    'Multiple': 'Y' if prop.multiple else 'N',
                    'Default': prop.default,
                    'Options': {
                        opt.code: opt.name for opt in (prop.optionsforselect.
                                                       all())
                    },
                } for prop in self.fields.filter(kind='PROPERTIES')
            },
            'RETURN_PROPERTIES': {
                prop.code: {
                    'Name': prop.name,
                    'Type': prop.type,
                    'Required': 'Y' if prop.required else 'N',
                    'Multiple': 'Y' if prop.multiple else 'N',
                    'Default': prop.default
                } for prop in self.fields.filter(kind='RETURN_PROPERTIES')
            }
        }


class FieldsActivity(models.Model):
    """Модель Поля активити."""
    KIND_PROPERTIES = [
        ('PROPERTIES', 'PROPERTIES'),
        ('RETURN_PROPERTIES', 'RETURN_PROPERTIES')
    ]

    TYPE_PROPERTIES = [
        ('string', 'Строка'),
        ('int', 'Целое число'),
        ('bool', 'Да/Нет'),
        ('date', 'Дата'),
        ('datetime', 'Дата/Время'),
        ('double', 'Число'),
        ('select', 'Список'),
        ('text', 'Текст'),
        ('user', 'Пользователь')
    ]

    code = models.CharField(
        max_length=50,
        verbose_name='Код',
    )
    kind = models.CharField(
        max_length=20,
        verbose_name='Вид',
        choices=KIND_PROPERTIES,
        default='PROPERTIES',
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Наименование',
    )
    type = models.CharField(
        max_length=10,
        verbose_name='Тип',
        choices=TYPE_PROPERTIES,
        default='string',
    )
    required = models.BooleanField(
        verbose_name='Обязательное',
        default=True,
    )
    multiple = models.BooleanField(
        verbose_name='Множественное',
        default=False
    )
    default = models.CharField(
        max_length=256,
        verbose_name='Значение по умолчанию',
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Поле активити'
        verbose_name_plural = 'Поля активити'


class OptionsForSelect(models.Model):
    """Модель Вариант для select."""
    code = models.CharField(
        max_length=20,
        verbose_name='Код варианта',
    )
    name = models.CharField(
        max_length=20,
        verbose_name='Наименование варианта',
    )
    fields = models.ForeignKey(
        FieldsActivity,
        on_delete=models.PROTECT,
        related_name='optionsforselect',
        verbose_name='Поле списка'
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Вариант для select'
        verbose_name_plural = 'Варианты для select'

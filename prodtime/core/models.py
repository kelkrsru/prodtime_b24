from django.db import models


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

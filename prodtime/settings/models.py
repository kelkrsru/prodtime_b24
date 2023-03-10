from django.db import models

from core.models import Portals


class SettingsPortal(models.Model):
    """Модель настроек портала"""

    portal = models.OneToOneField(
        Portals,
        verbose_name='Портал',
        related_name='settings_portal',
        on_delete=models.CASCADE,
    )
    create_deal = models.BooleanField(
        verbose_name='Создавать сделку',
        help_text='Создавать сделку при готовности товара с этим товаром?',
        default=True,
    )
    name_deal = models.CharField(
        verbose_name='Наименование сделки',
        help_text='Наименование создаваемой сделки',
        max_length=255,
        default='Новая сделка',
    )
    create_task = models.BooleanField(
        verbose_name='Создавать задачу',
        help_text='Создавать задачу к сделке',
        default=True,
    )
    name_task = models.CharField(
        verbose_name='Наименование задачи',
        help_text='Наименование создаваемой задачи к сделке',
        max_length=255,
        default='Новая задача',
    )
    task_deadline = models.IntegerField(
        verbose_name='Крайний срок задачи',
        help_text='Количество дней от текущей даты для крайнего срока задачи',
        default=3,
    )
    category_id = models.IntegerField(
        verbose_name='ID воронки продаж',
        help_text='ID воронки продаж, в которой создавать сделку',
        default=1,
    )
    stage_code = models.CharField(
        verbose_name='Стадия сделки',
        help_text='Стадия для создаваемой сделки',
        default='С2:NEW',
        max_length=20,
    )
    real_deal_code = models.CharField(
        verbose_name='Код поля реальной сделки',
        help_text='Код поля в создаваемой сделке, куда записывается ссылка на '
                  'реальную сделку',
        default='UF_CRM_0000000000',
        max_length=30,
    )
    section_list_id = models.IntegerField(
        verbose_name='ID списка сопоставления разделов',
        help_text='ID универсального списка сопоставления разделов для '
                  'копирования товаров каталога',
        default=1,
    )
    default_section_id = models.IntegerField(
        verbose_name='ID раздела по умолчанию',
        help_text='ID раздела по умолчанию, в который копируются товары без '
                  'сопоставления',
        default=1,
    )
    real_section_code = models.CharField(
        verbose_name='Код свойства реального раздела',
        help_text='Код свойства реального раздела в универсальном списке',
        default='PROPERTY_00',
        max_length=30,
    )
    copy_section_code = models.CharField(
        verbose_name='Код свойства раздела для копирования',
        help_text='Код свойства раздела для копирования в универсальном '
                  'списке',
        default='PROPERTY_00',
        max_length=30,
    )
    equivalent_code = models.CharField(
        verbose_name='Код свойства эквивалент',
        help_text='Код свойства эквивалент в каталоге товаров',
        default='PROPERTY_00',
        max_length=30,
    )
    sum_equivalent_code = models.CharField(
        verbose_name='Код свойства суммарный эквивалент',
        help_text='Код свойства суммарный эквивалент в сделке',
        default='UF_CRM_0000000000',
        max_length=30,
    )
    template_id = models.PositiveIntegerField(
        verbose_name='ID шаблона КП',
        help_text='ID шаблона коммерческого предложения',
        default=0,
    )
    kp_code = models.CharField(
        verbose_name='Код поля номеров КП',
        help_text='Код поля в сделке, куда записывается номера '
                  'сформированных коммерческих предложений',
        default='UF_CRM_0000000000',
        max_length=30,
    )
    kp_last_num_code = models.CharField(
        verbose_name='Код поля последнего номера КП',
        help_text='Код поля в сделке, куда записывается последний номер '
                  'сквозной нумерации коммерческих предложений',
        default='UF_CRM_0000000000',
        max_length=30,
    )
    smart_factory_number_id = models.PositiveIntegerField(
        verbose_name='ID smart процесса Заводские номера',
        help_text='ID smart процесса, в котором хранятся элементы с '
                  'заводскими номерами',
        default=0,
    )
    smart_factory_number_short_code = models.CharField(
        verbose_name='Текстовый код smart процесса Заводские номера',
        help_text='Текстовый код smart процесса Заводские номера',
        default='Tb4',
        max_length=10,
    )
    smart_factory_number_code = models.CharField(
        verbose_name='Код поля Заводской номер',
        help_text='Код поля Заводской номер в smart процессе',
        default='ufCrm0_0000000000000',
        max_length=30,
    )
    factory_number_code = models.CharField(
        verbose_name='Код свойства Заводской номер',
        help_text='Код свойства Заводской номер в каталоге товаров',
        default='PROPERTY_00',
        max_length=30,
    )
    responsible_id_copy_catalog = models.PositiveIntegerField(
        verbose_name='ID ответственного при копировании в каталог',
        help_text='ID ответственного сотрудника за созданный товар при '
                  'копировании его в каталог',
        default=1,
    )
    price_with_tax_code = models.CharField(
        verbose_name='Код свойства Цена с налогом',
        help_text='Код свойства Цена с налогом в каталоге товаров',
        default='PROPERTY_00',
        max_length=30,
    )
    is_auto_article_code = models.CharField(
        verbose_name='Код свойства Присваивать артикул автоматом',
        help_text='Код свойства Присваивать артикул автоматом в каталоге '
                  'товаров. Код, который отдает метод "catalog.product.get"',
        default='property83',
        max_length=30,
    )
    article_code = models.CharField(
        verbose_name='Код свойства Артикул',
        help_text='Код свойства Артикул в каталоге товаров. Код, который '
                  'отдает метод "catalog.product.get"',
        default='property84',
        max_length=30,
    )
    section_number_code = models.CharField(
        verbose_name='Код свойства Номер раздела',
        help_text='Код свойства Номер раздела в каталоге товаров. Код, '
                  'который отдает метод "catalog.product.get"',
        default='property85',
        max_length=30,
    )
    service_code = models.CharField(
        verbose_name='Код свойства Услуга',
        help_text='Код свойства Услуга в каталоге товаров. Код, '
                  'который отдает метод "catalog.product.get"',
        default='property87',
        max_length=30,
    )
    prodtime_str_code = models.CharField(
        verbose_name='Код свойства Срок производства',
        help_text='Код свойства Срок производства в каталоге товаров. Код, '
                  'который отдает метод "crm.product.get"',
        default='property88',
        max_length=30,
    )
    direct_costs_str_code = models.CharField(
        verbose_name='Код свойства Прямые затраты',
        help_text='Код свойства Прямые затраты в каталоге товаров. Код, '
                  'который отдает метод "crm.product.get"',
        default='property00',
        max_length=30,
    )
    standard_hours_str_code = models.CharField(
        verbose_name='Код свойства Нормочасы',
        help_text='Код свойства Нормочасы в каталоге товаров. Код, '
                  'который отдает метод "crm.product.get"',
        default='property00',
        max_length=30,
    )
    materials_str_code = models.CharField(
        verbose_name='Код свойства Материалы',
        help_text='Код свойства Материалы в каталоге товаров. Код, '
                  'который отдает метод "crm.product.get"',
        default='property00',
        max_length=30,
    )
    is_admin_code = models.CharField(
        verbose_name='Код свойства Администратор приложения',
        help_text='Код свойства Администратор приложения в пользователях '
                  'Битрикс24',
        default='UF_USR_1678006529399',
        max_length=30,
    )

    class Meta:
        verbose_name = 'Настройка портала'
        verbose_name_plural = 'Настройки портала'

        ordering = ['portal', 'pk']

    def __str__(self):
        return 'Настройки для портала {}'.format(self.portal.name)


class Numeric(models.Model):
    """Модель настроек нумерации внутри года."""

    portal = models.ForeignKey(
        Portals,
        verbose_name='Портал',
        related_name='numeric_portal',
        on_delete=models.CASCADE,
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год',
        help_text='Год нумерации',
    )
    last_number = models.PositiveSmallIntegerField(
        verbose_name='Последний номер',
        help_text='Последний номер в данном году',
        default=0,
    )

    class Meta:
        verbose_name = 'Настройка нумерации'
        verbose_name_plural = 'Настройки нумерации'

        ordering = ['portal', 'year']

    def __str__(self):
        return 'Настройки для года {}'.format(self.year)


class AssociativeYearNumber(models.Model):
    """Модель соответствия между годом и его кодом."""

    portal = models.ForeignKey(
        Portals,
        verbose_name='Портал',
        related_name='associative_portal',
        on_delete=models.CASCADE,
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год',
    )
    year_code = models.CharField(
        verbose_name='Код года',
        max_length=20,
    )

    class Meta:
        verbose_name = 'Код года'
        verbose_name_plural = 'Коды года'

        ordering = ['portal', 'year']

    def __str__(self):
        return 'Код для года {}'.format(self.year)




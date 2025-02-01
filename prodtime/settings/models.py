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
    create_smart = models.BooleanField(
        'Создавать элемент смарт процесса',
        help_text='Создавать элемент смарт процесса при нажатии на кнопку "Выпуск"',
        default=True,
    )
    id_smart = models.PositiveSmallIntegerField(
        'ID смарт процесса',
        help_text='ID смарт процесса для создания элемента',
        default=1
    )
    code_smart = models.CharField(
        'Код смарт процесса',
        help_text='Код смарт процесса для создания элемента, данный код можно получить методом REST API '
                  '"crm.enum.ownertype"',
        default='Tb1',
        max_length=20
    )
    name_smart = models.CharField(
        'Наименование элемента',
        help_text='Наименование создаваемого элемента смарт процесса',
        max_length=255,
        default='Новая отгрузка',
    )
    stage_smart = models.CharField(
        'Стадия смарт процесса',
        help_text='Стадия для создаваемого элемента смарт процесса',
        default='С2:NEW',
        max_length=20,
    )
    real_deal_code_smart = models.CharField(
        'Код поля реальной сделки в смарт процессе',
        help_text='Код поля в создаваемом элементе смарт процесса, куда записывается ссылка на реальную сделку',
        default='ufCrm00_0000000000',
        max_length=30,
    )
    sum_direct_costs_code_smart = models.CharField(
        verbose_name='Код поля Сумма прямых затрат в смарт процессе',
        help_text='Код поля Сумма прямых затрат в создаваемом элементе смарт процесса',
        default='ufCrm00_0000000000',
        max_length=30,
    )
    sum_direct_costs_fact_code_smart = models.CharField(
        verbose_name='Код поля Сумма фактических затрат в смарт процессе',
        help_text='Код поля Сумма фактических затрат в создаваемом элементе смарт процесса',
        default='ufCrm00_0000000000',
        max_length=30,
    )
    sum_equivalent_code_smart = models.CharField(
        verbose_name='Код поля Суммарный эквивалент в смарт процессе',
        help_text='Код поля Суммарный эквивалент в создаваемом элементе смарт процесса',
        default='ufCrm00_0000000000',
        max_length=30,
    )
    max_prodtime_smart = models.CharField(
        verbose_name='Код поля Максимальный срок производства в смарт процессе',
        help_text='Код поля Максимальный срок производства в создаваемом элементе смарт процесса',
        default='ufCrm00_0000000000',
        max_length=30,
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
    sum_equivalent_quote_code = models.CharField(
        verbose_name='Код свойства суммарный эквивалент в предложении',
        help_text='Код свойства суммарный эквивалент в предложении',
        default='UF_CRM_0000000000',
        max_length=30,
    )
    sum_direct_costs_code = models.CharField(
        verbose_name='Код поля Сумма прямых затрат',
        help_text='Код поля Сумма прямых затрат в сделке',
        default='UF_CRM_0000000000',
        max_length=30,
    )
    sum_direct_costs_fact_code = models.CharField(
        verbose_name='Код поля Сумма фактических затрат',
        help_text='Код поля Сумма фактических затрат в сделке',
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
    direct_costs_code = models.CharField(
        verbose_name='Код свойства Прямые затраты',
        help_text='Код свойства Прямые затраты в каталоге товаров. Код, '
                  'который отдает метод "crm.product.get"',
        default='property90',
        max_length=30,
    )
    standard_hours_code = models.CharField(
        verbose_name='Код свойства Нормочасы',
        help_text='Код свойства Нормочасы в каталоге товаров. Код, '
                  'который отдает метод "crm.product.get"',
        default='property91',
        max_length=30,
    )
    materials_code = models.CharField(
        verbose_name='Код свойства Материалы',
        help_text='Код свойства Материалы в каталоге товаров. Код, '
                  'который отдает метод "crm.product.get"',
        default='property92',
        max_length=30,
    )
    # income_code = models.CharField(
    #     verbose_name='Код свойства Прибыль, %',
    #     help_text='Код свойства Прибыль (план) в каталоге товаров. Код, '
    #               'который отдает метод "catalog.product.get"',
    #     default='property357',
    #     max_length=30,
    # )
    income_percent = models.DecimalField(
        verbose_name='Процент плановой прибыли',
        help_text='Процент плановой прибыли для всех товаров, %',
        max_digits=5,
        decimal_places=1,
        default=1
    )
    deal_field_code_income_res = models.CharField(
        verbose_name='Код поля в сделки для расчета прибыли',
        help_text='Код в сделке. При заполненности поля рассчитывается прибыль при открытии приложения.',
        default='UF_CRM_1652693659',
        max_length=30,
    )
    is_admin_code = models.CharField(
        verbose_name='Код свойства Администратор приложения',
        help_text='Код свойства Администратор приложения в пользователях '
                  'Битрикс24',
        default='UF_USR_1678006529399',
        max_length=30,
    )
    max_prodtime_code = models.CharField(
        verbose_name='Код свойства Максимальный срок производства',
        help_text='Код свойства Максимальный срок производства в сделке',
        default='UF_CRM_1678710729823',
        max_length=30,
    )
    num_invoice_code = models.CharField('Код свойства Номер счета', help_text='Код свойства Номер счета в сделке',
                                        default='UF_CRM_1661507258282', max_length=30, )
    token = models.CharField('Токен', help_text='Токен для обновления сделки через webhook',
                             default='eQQOKDYMN?DY3IXy6aae9GB0AF2wtk30xtDyLo=2OIFo6HSuDVDf2h0=52BS3Xx4', max_length=256)

    class Meta:
        verbose_name = 'Настройка портала'
        verbose_name_plural = 'Настройки портала'

        ordering = ['portal', 'pk']

    def __str__(self):
        return 'Настройки для портала {}'.format(self.portal.name)


class SettingsForReportStock(models.Model):
    """Модель настроек для отчета по остаткам"""

    class ColorBackground(models.TextChoices):
        PRIMARY = 'bg-primary', 'Синий'
        SECONDARY = 'bg-secondary', 'Серый'
        SUCCESS = 'bg-success', 'Зеленый'
        DANGER = 'bg-danger', 'Красный'
        DARK = 'bg-dark', 'Черный'

    portal = models.OneToOneField(
        Portals,
        verbose_name='Портал',
        related_name='settings_for_report_stock',
        on_delete=models.CASCADE,
    )
    stock_id = models.PositiveSmallIntegerField(
        'ID склада',
        help_text='ID склада для работы отчета',
        default=1,
    )
    min_stock_code = models.CharField(
        verbose_name='Код свойства Минимальный остаток',
        help_text='Код свойства Минимальный остаток в каталоге товаров. Код, который отдает метод '
                  '"catalog.product.get"',
        default='property00',
        max_length=30,
    )
    max_stock_code = models.CharField(
        verbose_name='Код свойства Максимальное количество',
        help_text='Код свойства Максимальное количество в каталоге товаров. Код, который отдает метод '
                  '"catalog.product.get"',
        default='property00',
        max_length=30,
    )
    create_task = models.BooleanField(
        verbose_name='Создавать задачу',
        help_text='Создавать задачу при достижении минимального остатка',
        default=True,
    )
    name_task = models.CharField(
        verbose_name='Наименование задачи',
        help_text='Наименование создаваемой задачи при достижении минимального остатка',
        max_length=255,
        default='Новая задача',
    )
    text_task = models.TextField(
        verbose_name='Текст задачи',
        help_text='Текст создаваемой задачи при достижении минимального остатка',
        blank=True,
    )
    task_deadline = models.IntegerField(
        verbose_name='Крайний срок задачи',
        help_text='Количество дней от текущей даты для крайнего срока задачи',
        default=3,
    )
    task_project_id = models.PositiveSmallIntegerField(
        'ID проекта задачи',
        help_text='ID проекта битрикс24, к которому будет относиться задача',
        default=0
    )
    task_responsible_code = models.CharField(
        verbose_name='Код свойства ответственного',
        help_text='Код свойства товара в каталоге товаров, из которого берется ID ответственного за создаваемую задачу',
        default='property00',
        max_length=30,
    )
    task_responsible_default_id = models.PositiveSmallIntegerField(
        'ID ответственного сотрудника',
        help_text='ID ответственного за задачу сотрудника по умолчанию, если поле в каталоге товаров не заполнено',
        default=1,
    )
    task_responsible_default_always = models.BooleanField(
        'Всегда ответственный по умолчанию',
        help_text='Всегда подставлять ответственным за задачу по умолчанию, не смотря на заполненность поля в каталоге '
                  'товаров',
        default=False,
    )
    task_id_code = models.CharField(
        verbose_name='Код свойства ID задачи',
        help_text='Код свойства ID задачи в каталоге товаров, в которое записывается ID созданной задачи',
        default='property00',
        max_length=30,
    )
    background_row = models.CharField(
        'Цвет выделения строк Min',
        help_text='Цвет выделения строк, у которых достигнуто значение минимального остатка',
        max_length=30,
        choices=ColorBackground.choices,
        default=ColorBackground.DANGER
    )
    background_row_max = models.CharField(
        'Цвет выделения строк Max',
        help_text='Цвет выделения строк, у которых значение больше максимального остатка',
        max_length=30,
        choices=ColorBackground.choices,
        default=ColorBackground.SUCCESS
    )

    class Meta:
        verbose_name = 'Настройка для отчета по Остаткам'
        verbose_name_plural = 'Настройки для отчета по Остаткам'

        ordering = ['portal', 'pk']

    def __str__(self):
        return f'Настройки отчета по Остаткам для портала {self.portal.name}'


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

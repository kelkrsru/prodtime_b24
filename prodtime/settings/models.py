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

    class Meta:
        verbose_name = 'Настройка портала'
        verbose_name_plural = 'Настройки портала'

        ordering = ['portal', 'pk']

    def __str__(self):
        return 'Настройки для портала {}'.format(self.portal.name)


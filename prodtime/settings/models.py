from django.db import models

from core.models import Portals


class SettingsPortal(models.Model):
    """Модель настроек портала"""

    portal = models.ForeignKey(
        Portals,
        verbose_name='Портал',
        related_name='settings_portal',
        on_delete=models.CASCADE,
        unique=True,
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

    class Meta:
        verbose_name = 'Настройка портала'
        verbose_name_plural = 'Настройки портала'

        ordering = ['portal', 'pk']

    def __str__(self):
        return 'Настройки для портала {}'.format(self.portal.name)


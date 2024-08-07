import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.bitrix24.bitrix24 import create_portal, TaskB24, ProductInCatalogB24
from reports.ReportProdtime import ReportStock

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):

        portal = create_portal('5acee3964adf8fd166051d9f5d5214e2')
        report_stock = ReportStock(portal)
        separator = '*' * 40

        def check_tack(product, action, portal_obj, settings_for_report_stock):
            if 'task_id' not in product:
                logger.info(f'Для товара id={product.get("productId")} задачи нет')
                if action == 'create':
                    logger.info(f'Для товара id={product.get("productId")} СТАВИМ ЗАДАЧУ')
                    task = _create_task(portal_obj, settings_for_report_stock, product)
                    if not task:
                        logger.warning(f'Для товара id={product.get("productId")} НЕ поставлена задача')
                    if 'error' in task:
                        logger.error(f'Ошибка постановки задачи: {task.get("error")} - {task.get("error_description")}')
                        logger.warning(f'Для товара id={product.get("productId")} НЕ поставлена задача')
                    logger.info(f'Для товара id={product.get("productId")} поставлена задача {task.get("result").get("task").get("id")}')
                    _update_product(portal_obj, settings_for_report_stock, product, task.get("result").get("task").get("id"))
            else:
                logger.info(f'Для товара id={product.get("productId")} задача уже поставлена id={product.get("task_id")}')
                if action == 'delete':
                    logger.info(f'Для товара id={product.get("productId")} УДАЛЯЕМ ID ЗАДАЧИ из свойств каталога')
                    _update_product(portal_obj, settings_for_report_stock, product, None)

        def _create_task(portal_obj, settings_for_report_stock, product):
            """Метод создания необходимой задачи в Б24."""
            deadline = settings_for_report_stock.task_deadline
            deadline = timezone.now() + timezone.timedelta(days=deadline)
            if not product.get('task_responsible'):
                logger.warning(f'Для товара id={product.get("productId")} не указан ответственный. Задача не поставлена.')
                return None
            fields = {
                'TITLE': settings_for_report_stock.name_task,
                'DESCRIPTION': settings_for_report_stock.text_task,
                'RESPONSIBLE_ID': product.get('task_responsible'),
                'DEADLINE': deadline.isoformat(),
                'MATCH_WORK_TIME': 'Y',
            }
            logger.info(f'{fields=}')
            bx24_task = TaskB24(portal_obj, 0)
            return bx24_task.create(fields)

        def _update_product(portal_obj, settings_for_report_stock, product, task_id):
            """Метод для обновления полей в продукте каталога."""
            product_in_catalog = ProductInCatalogB24(portal_obj, product.get('productId'))
            if task_id:
                product_in_catalog.properties[settings_for_report_stock.task_id_code] = {}
                product_in_catalog.properties[settings_for_report_stock.task_id_code]['value'] = task_id
            else:
                product_in_catalog.properties[settings_for_report_stock.task_id_code] = None
            product_in_catalog.check_and_update_properties()
            product_in_catalog.update(product_in_catalog.properties)

        for remain_product in report_stock.remains_products:
            if remain_product.get("no_available") == "-":
                logger.info(f'Количества товара id={remain_product.get("productId")} достаточное количество на складе')
                check_tack(remain_product, 'delete', portal, report_stock.settings_for_report_stock)
                logger.info(f'{separator}')
                continue
            logger.info(f'Количества товара id={remain_product.get("productId")} не хватает до минимального остатка {remain_product.get("no_available")}')

            check_tack(remain_product, 'create', portal, report_stock.settings_for_report_stock)

            logger.info(f'{separator}')


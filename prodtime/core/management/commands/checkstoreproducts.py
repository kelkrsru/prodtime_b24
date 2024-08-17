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
                    logger.info(f'Для товара id={product.get("productId")} поставлена задача '
                                f'{task.get("result").get("task").get("id")}')
                    _update_product(portal_obj, settings_for_report_stock, product,
                                    task.get("result").get("task").get("id"))
            else:
                logger.info(f'Для товара id={product.get("productId")} задача уже поставлена '
                            f'id={product.get("task_id")}')
                if action == 'delete':
                    logger.info(f'Для товара id={product.get("productId")} УДАЛЯЕМ ID ЗАДАЧИ из свойств каталога')
                    _update_product(portal_obj, settings_for_report_stock, product, None)

        def _create_task(portal_obj, settings_for_report_stock, product):
            """Метод создания необходимой задачи в Б24."""
            deadline = settings_for_report_stock.task_deadline
            deadline = timezone.now() + timezone.timedelta(days=deadline)
            fields = {
                'TITLE': _replace_values(settings_for_report_stock.name_task, product, portal_obj),
                'DESCRIPTION': _replace_values(settings_for_report_stock.text_task, product, portal_obj),
                'RESPONSIBLE_ID': _get_responsible_task(settings_for_report_stock, product),
                'DEADLINE': deadline.isoformat(),
                'MATCH_WORK_TIME': 'Y',
            }
            if settings_for_report_stock.task_project_id:
                fields['GROUP_ID'] = settings_for_report_stock.task_project_id
            logger.info(f'{fields=}')
            bx24_task = TaskB24(portal_obj, 0)
            return bx24_task.create(fields)

        def _replace_values(value, product, portal_obj):
            """Метод для замены переменных в тексте и наименовании задачи."""
            value = value.replace('{ProductName}', product.get('name'))
            value = value.replace('{ProductMin}', str(product.get('min_stock')))
            value = value.replace('{ProductAvailable}', str(product.get('quantityAvailable')))
            value = value.replace('{ProductNoAvailable}', str(product.get('no_available')))
            link = f'https://{portal_obj.name}/crm/catalog/15/product/{product.get("productId")}/'
            value = value.replace('{ProductLink}', link)
            return value

        def _get_responsible_task(settings_for_report_stock, product):
            if settings_for_report_stock.task_responsible_default_always or not product.get('task_responsible'):
                return settings_for_report_stock.task_responsible_default_id
            return product.get('task_responsible')

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
            logger.info(f'Количества товара id={remain_product.get("productId")} не хватает до минимального '
                        f'остатка {remain_product.get("no_available")}')

            check_tack(remain_product, 'create', portal, report_stock.settings_for_report_stock)

            logger.info(f'{separator}')

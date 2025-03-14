import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.bitrix24.bitrix24 import create_portal, TaskB24, ProductInCatalogB24
from reports.ReportProdtime import ReportStock

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):

        portal = create_portal('895413ed6c89998e579c7d38f4faa520')
        report_stock = ReportStock(portal, None)
        separator = '*' * 40

        def check_tack(product, action, portal_obj, settings_for_report_stock, flag):
            """Метод для проверки задачи."""
            add_attr = '' if flag == 'min' else '_average'
            flag_str = 'минимального' if flag == 'min' else 'среднего'
            if action == 'delete':
                logger.info(f'Для товара id={product.get("productId")} УДАЛЯЕМ ЗАДАЧУ')
                logger.info(f'Передан flag={flag}')
                if (('task_id' not in product and flag == 'min') or
                        ('task_average_id' not in product and flag == 'average')):
                    logger.info(f'Для товара id={product.get("productId")} задача для {flag_str} '
                                f'остатка не поставлена ранее. Удаление не требуется.')
                    return
                logger.info(f'Для товара id={product.get("productId")} УДАЛИЛИ ID ЗАДАЧИ {flag_str} остатка из '
                            f'свойств каталога')
                _update_product(portal_obj, settings_for_report_stock, product, None, flag)
            if action == 'create':
                logger.info(f'Для товара id={product.get("productId")} СТАВИМ ЗАДАЧУ')
                if not getattr(settings_for_report_stock, f'create_task{add_attr}'):
                    logger.info(f'Для {flag_str} остатка постановка задачи отключена в настройках. '
                                f'Задача НЕ поставлена')
                    return
                logger.info(f'Передан flag={flag}')
                if ('task_id' in product and flag == 'min') or ('task_average_id' in product and flag == 'average'):
                    logger.info(f'Для товара id={product.get("productId")} УЖЕ поставлена задача для {flag_str} '
                                f'остатка, новая не требуется.')
                    return
                task = _create_task(portal_obj, settings_for_report_stock, product, flag)
                if not task:
                    logger.warning(f'Для товара id={product.get("productId")} НЕ поставлена задача')
                if 'error' in task:
                    logger.error(f'Ошибка постановки задачи: {task.get("error")} - {task.get("error_description")}')
                    logger.warning(f'Для товара id={product.get("productId")} НЕ поставлена задача')
                logger.info(f'Для товара id={product.get("productId")} поставлена задача {flag_str} остатка id='
                            f'{task.get("result").get("task").get("id")}')
                _update_product(portal_obj, settings_for_report_stock, product,
                                task.get("result").get("task").get("id"), flag)

        def _create_task(portal_obj, settings_for_report_stock, product, flag):
            """Метод создания необходимой задачи в Б24."""
            add_attr = '' if flag == 'min' else '_average'
            deadline = getattr(settings_for_report_stock, f'task{add_attr}_deadline')
            deadline = (timezone.now() + timezone.timedelta(days=deadline)).isoformat()
            fields = {
                'TITLE': _replace_values(getattr(settings_for_report_stock, f'name_task{add_attr}'), product,
                                         portal_obj),
                'DESCRIPTION': _replace_values(getattr(settings_for_report_stock, f'text_task{add_attr}'), product,
                                               portal_obj),
                'RESPONSIBLE_ID': _get_responsible_task(settings_for_report_stock, product, flag),
                'CREATED_BY': _get_responsible_task(settings_for_report_stock, product, flag),
                'DEADLINE': deadline,
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
            value = value.replace('{ProductMax}', str(product.get('max_stock')))
            value = value.replace('{ProductAvailable}', str(product.get('quantityAvailable')))
            value = value.replace('{ProductNoAvailable}', str(product.get('no_available')))
            link = f'https://{portal_obj.name}/crm/catalog/15/product/{product.get("productId")}/'
            value = value.replace('{ProductLink}', link)
            return value

        def _get_responsible_task(settings_for_report_stock, product, flag):
            add_attr = '' if flag == 'min' else '_average'
            responsible_default_always = getattr(settings_for_report_stock,
                                                 f'task{add_attr}_responsible_default_always')
            responsible_default_id = getattr(settings_for_report_stock, f'task{add_attr}_responsible_default_id')
            if responsible_default_always or not product.get('task_responsible'):
                return responsible_default_id
            return product.get('task_responsible')

        def _update_product(portal_obj, settings_for_report_stock, product, task_id, flag):
            """Метод для обновления полей в продукте каталога."""
            product_in_catalog = ProductInCatalogB24(portal_obj, product.get('productId'))
            add_attr = '' if flag == 'min' else '_average'
            if task_id:
                product_in_catalog.properties[getattr(settings_for_report_stock, f'task{add_attr}_id_code')] = {}
                product_in_catalog.properties[getattr(settings_for_report_stock,
                                                      f'task{add_attr}_id_code')]['value'] = task_id
            else:
                product_in_catalog.properties[getattr(settings_for_report_stock, f'task{add_attr}_id_code')] = None
            product_in_catalog.check_and_update_properties()
            product_in_catalog.update(product_in_catalog.properties)

        for remain_product in report_stock.remains_products:
            if not remain_product.get("flag_task") and not remain_product.get("flag_task_average"):
                logger.info(f'Количества товара id={remain_product.get("productId")} достаточное количество на складе')
                check_tack(remain_product, 'delete', portal, report_stock.settings_for_report_stock, 'min')
                check_tack(remain_product, 'delete', portal, report_stock.settings_for_report_stock, 'average')
                logger.info(f'{separator}')
                continue
            if not remain_product.get("flag_task") and remain_product.get("flag_task_average"):
                logger.info(f'Количества товара id={remain_product.get("productId")} не хватает до среднего остатка')
                check_tack(remain_product, 'create', portal, report_stock.settings_for_report_stock, 'average')
                logger.info(f'{separator}')
                continue
            logger.info(f'Количества товара id={remain_product.get("productId")} не хватает до минимального '
                        f'остатка {remain_product.get("no_available")}')
            check_tack(remain_product, 'create', portal, report_stock.settings_for_report_stock, 'min')

            logger.info(f'{separator}')

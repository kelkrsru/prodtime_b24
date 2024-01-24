import decimal
import csv
from pprint import pprint

from django.core.management.base import BaseCommand

from core.bitrix24.bitrix24 import create_portal, ProductInCatalogB24
from settings.models import SettingsPortal


class Command(BaseCommand):
    def handle(self, *args, **options):

        portal = create_portal('895413ed6c89998e579c7d38f4faa520')
        settings_portal = SettingsPortal.objects.get(portal=portal)
        data_in = {155: decimal.Decimal(10)}

        with open('/home/bitrix/catalog.csv', newline='') as csvfile:
            with open('/home/bitrix/catalog.log', 'w') as logfile:
                reader = csv.DictReader(csvfile)
                i = 0
                for row in reader:
                    i += 1
                    # if i > 3:
                    #     break
                    id_section = row.get('iblockSectionId')
                    id_product = row.get('id')
                    name_product = row.get('name')
                    percent = row.get('Процент прибыли')
                    print(i)
                    try:
                        percent = int(percent)
                    except ValueError:
                        logfile.write(f'{i}. Для товара {id_section=} {id_product=} {name_product=} процент НЕ установлен {percent=}\n')
                        continue
                    update_product = ProductInCatalogB24(portal, id_product)
                    result = update_product.update({settings_portal.income_code: {"value": str(percent)}})
                    logfile.write(f'{i}. Для товара {id_section=} {id_product=} {name_product=} процент установлен {percent=}\n')

        # for item in data_in:
        #     print(f'{item=}')
        #     select_user = ['iblockId', 'iblockSectionId', 'id', 'name', settings_portal.income_code]
        #     filter_user = {'iblockId': 15, 'iblockSectionId': item}
        #     products = ProductInCatalogB24(portal, 0).get_all_products_in_section(select_user, filter_user)
        #     print(len(products))
        #     for product in products:
        #         update_product = ProductInCatalogB24(portal, product.get('id'))
        #         result = update_product.update({settings_portal.income_code: {"value": str(data_in[item])}})

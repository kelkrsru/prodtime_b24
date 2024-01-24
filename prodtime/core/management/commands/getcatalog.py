import csv

from django.core.management.base import BaseCommand

from core.bitrix24.bitrix24 import create_portal, ProductInCatalogB24, CatalogSectionB24
from settings.models import SettingsPortal


class Command(BaseCommand):
    def handle(self, *args, **options):

        portal = create_portal('895413ed6c89998e579c7d38f4faa520')
        settings_portal = SettingsPortal.objects.get(portal=portal)

        select_user = ['iblockId', 'iblockSectionId', 'id', 'name', settings_portal.income_code]
        filter_user = {'iblockId': 15}
        products = ProductInCatalogB24(portal, 0).get_all_products_in_section(select_user, filter_user)
        sections = {}

        with open('/home/bitrix/test.csv', 'w', newline='') as csvfile:
            headers = list(products[0].keys())
            headers.append('iblockSectionName')
            writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            count = 0
            for product in products:
                section = CatalogSectionB24(portal, product.get('iblockSectionId'))
                section = section.properties.get('section')
                section_id = section.get('id')
                if section_id not in sections:
                    sections[section_id] = section.get('name')
                product['iblockSectionName'] = sections.get(section_id)
                writer.writerow(product)
                count += 1
                print(count)

from django.core.management.base import BaseCommand

from core.bitrix24.bitrix24 import DealB24, create_portal, UserB24
from core.models import Responsible
from dealcard.models import Deal


class Command(BaseCommand):
    def handle(self, *args, **options):

        deals = Deal.objects.all()
        # deals = Deal.objects.filter(pk__in=[1, 2, 3])
        portal = create_portal('895413ed6c89998e579c7d38f4faa520')
        for deal in deals:
            print(deal.deal_id)
            try:
                deal_bx = DealB24(portal, deal.deal_id)
                deal.invoice_number = deal_bx.properties.get('UF_CRM_1661507258282')
                deal.save()
                print(deal.invoice_number)
                print('ok')
            except RuntimeError:
                print('not found')
                continue

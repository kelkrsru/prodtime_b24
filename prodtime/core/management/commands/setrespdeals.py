from django.core.management.base import BaseCommand

from core.bitrix24.bitrix24 import DealB24, create_portal, UserB24
from core.models import Responsible
from dealcard.models import Deal


class Command(BaseCommand):
    def handle(self, *args, **options):

        deals = Deal.objects.all()
        portal = create_portal('895413ed6c89998e579c7d38f4faa520')
        for deal in deals:
            print(deal.deal_id)
            try:
                deal_bx = DealB24(portal, deal.deal_id)
                responsible_id = int(deal_bx.responsible)
                responsible_b24 = UserB24(portal, responsible_id)
                responsible, created = Responsible.objects.get_or_create(
                    id_b24=responsible_id,
                    defaults={
                        'first_name': responsible_b24.properties[0].get('NAME'),
                        'last_name': responsible_b24.properties[0].get('LAST_NAME'),
                        'position': responsible_b24.properties[0].get('WORK_POSITION'),
                    },
                )
                deal.responsible = responsible
                deal.save()
                print('ok')
            except RuntimeError:
                print('not found')
                continue

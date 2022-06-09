from django.core.management import BaseCommand
from django.db import transaction
from model_bakery import baker


class Command(BaseCommand):

    def handle(self, *args, **options):
        with transaction.atomic():
            baker_objs = baker.make('practice.Machine', _quantity=300)

            for obj in baker_objs:
                baker.make('practice.History', machine=obj, _quantity=1000)

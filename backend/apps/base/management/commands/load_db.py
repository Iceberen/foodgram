import csv

from apps.base.models import Ingredient
from core.settings import BASE_DIR
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'import db from csv'

    def handle(self, *args, **options):
        with open(f'{BASE_DIR}/data/ingredients.csv', encoding='utf-8') as db:
            data = csv.reader(db)
            next(data)

            Ingredient.objects.all().delete()

            for row in data:
                ingredient = Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                ingredient.save()

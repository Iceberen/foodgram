import csv

from apps.recipe.models import Ingredient
from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR


class Command(BaseCommand):
    help = 'import db from csv'

    def handle(self, *args, **options):
        with open(f'{BASE_DIR}/data/ingredients.csv', encoding='utf-8') as db:
            data = csv.reader(db)
            next(data)

            for row in data:
                ingredient, _ = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
            ingredient.save()

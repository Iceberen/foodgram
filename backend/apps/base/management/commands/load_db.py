import csv

from django.core.management.base import BaseCommand
from apps.base.models import Ingredient


class Command(BaseCommand):
    help = 'import db from csv'

    def handle(self, *args, **options):
        with open('static/data/ingredients.csv', encoding='utf-8') as db:
            data = csv.reader(db)
            next(data)

            Ingredient.objects.all().delete()

            for row in data:
                ingredient = Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                ingredient.save()

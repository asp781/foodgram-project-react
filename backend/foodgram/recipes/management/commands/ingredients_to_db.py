import codecs
import csv
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from recipes.models import Ingredient


class Command(BaseCommand):

    filename = 'ingredients.csv'

    def handle(self, *args, **options):
        with codecs.open(
            f'../../data/{self.filename}', 'r', encoding='utf-8'
        ) as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                try:
                    Ingredient.objects.create(
                        name=row[0], measurement_unit=row[1]
                    )
                except (ValueError):
                    pass
                except (IntegrityError):
                    pass
            self.stdout.write(f'Данные из {self.filename} загружены')

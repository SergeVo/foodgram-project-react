import csv
from os import path

from django.core.management.base import BaseCommand
from foodgram.settings import STATIC_ROOT
from recipes.models import Ingredient


class Command(BaseCommand):
    """Обработчик менеджмент-команды по импорту csv-данных в БД."""

    def handle(self, *args, **options):
        data_path = path.join(STATIC_ROOT, 'data')
        self.import_ingredients(path.join(data_path, 'ingredients.csv'))

    def import_csv_file(self, conn, table_name, csv_file):
        cur = conn.cursor()
        header = ''
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.reader(read_file)
            for row in reader:
                if header == '':
                    header = ','.join(row)
                    col_count = len(row)
                    questions = ['?'] * col_count
                    questions_str = ','.join(questions)
                else:
                    insert_sql_str = (
                        f'INSERT INTO {table_name} ({header}) '
                        f'VALUES ({questions_str});'
                    )
                    self.stdout.write(insert_sql_str)
                    cur.execute(insert_sql_str, row)
        conn.commit()

    def import_ingredients(self, csv_file):
        Ingredient.objects.all().delete()
        with open(csv_file, 'r', encoding='utf-8') as read_file:
            reader = csv.DictReader(read_file)
            id = 1
            for row in reader:
                Ingredient.objects.get_or_create(
                    id=id,
                    name=row['name'],
                    measurement_unit=row['measurement_unit'],
                )
                id += 1

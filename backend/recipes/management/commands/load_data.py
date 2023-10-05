import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    ''' Загрузка данных из JSON-файла '''

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Загружаем ингридиенты!'))
        ingredients_file_path = 'data/ingredients.json'
        try:
            with open(ingredients_file_path,
                      encoding='utf-8') as data_file_ingredients:
                ingredient_data = json.load(data_file_ingredients)
                for ingredients in ingredient_data:
                    Ingredient.objects.get_or_create(**ingredients)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('Файл с ингредиентами не найден!'))
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(
                    'Ошибка при чтении JSON файла с ингредиентами!'))

        self.stdout.write(self.style.WARNING('Загружаем тэги!'))
        tags_file_path = 'data/tags.json'
        try:
            with open(tags_file_path, encoding='utf-8') as data_file_tags:
                tags_data = json.load(data_file_tags)
                for tags in tags_data:
                    Tag.objects.get_or_create(**tags)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Файл с тегами не найден!'))
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('Ошибка при чтении JSON файла с тегами!'))

        self.stdout.write(self.style.SUCCESS('Отлично загрузили!'))

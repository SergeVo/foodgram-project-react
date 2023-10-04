import json
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    ''' Загрузка данных из JSON-файла '''

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Загружаем ингридиенты!'))
        ingredients_file_path = 'data/ingredients.json'
        if os.path.exists(ingredients_file_path):
            with open(ingredients_file_path,
                      encoding='utf-8') as data_file_ingredients:
                ingredient_data = json.load(data_file_ingredients)
                for ingredients in ingredient_data:
                    Ingredient.objects.get_or_create(**ingredients)
        else:
            self.stdout.write(
                self.style.ERROR('Файл с ингредиентами не найден!'))

        self.stdout.write(self.style.WARNING('Загружаем тэги!'))
        tags_file_path = 'data/tags.json'
        if os.path.exists(tags_file_path):
            with open(tags_file_path, encoding='utf-8') as data_file_tags:
                tags_data = json.load(data_file_tags)
                for tags in tags_data:
                    Tag.objects.get_or_create(**tags)
        else:
            self.stdout.write(self.style.ERROR('Файл с тегами не найден!'))

        self.stdout.write(self.style.SUCCESS('Отлично загрузили!'))

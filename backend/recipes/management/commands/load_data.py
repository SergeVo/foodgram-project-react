import json
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Загрузка данных из JSON-файла"""

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Загружаем!"))

        file_path = "data/ingredients.json"
        if os.path.exists(file_path):

            with open(
                "data/ingredients.json",
                encoding="utf-8",
            ) as data_file_ingredients:
                ingredient_data = json.loads(data_file_ingredients.read())
                for ingredients in ingredient_data:
                    Ingredient.objects.get_or_create(**ingredients)

            with open(
                "data/tags.json",
                encoding="utf-8",
            ) as data_file_tags:
                tags_data = json.loads(data_file_tags.read())
                for tags in tags_data:
                    Tag.objects.get_or_create(**tags)

            self.stdout.write(self.style.SUCCESS("Отлично загрузили!"))
        else:
            self.stdout.write(self.style.ERROR("Файлы не найдены!"))

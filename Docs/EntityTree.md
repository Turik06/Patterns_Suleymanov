# Структура связей моделей (EntityTree)

## 1. Связи единиц измерения (range_model)

Единицы измерения ссылаются друг на друга по цепочке через поле `base_range` (от большей к меньшей базовой):

```mermaid
graph LR
    Ton[Тонна, коэф 1000] -->|base_range| Kg[Килограмм, коэф 1000]
    Kg -->|base_range| Gram[Грамм, коэф 1]
    Liter[Литр, коэф 1000] -->|base_range| ML[Миллилитр, коэф 1]
    Piece[Штука, коэф 1]
```

В JSON это раскрывается во вложенные объекты:
```json
{
  "name": "Тонна",
  "conversion_factor": 1000,
  "base_range": {
    "name": "Килограмм",
    "conversion_factor": 1000,
    "base_range": {
      "name": "Грамм",
      "conversion_factor": 1,
      "base_range": null
    }
  }
}
```

---

## 2. Составные рецепты (recipe_model)

В рецепте есть список строк `rows`. Строка может содержать обычный ингредиент, либо полуфабрикат — то есть другой рецепт (`sub_recipe`):

```mermaid
graph TD
    Pancakes[Рецепт: Блины] --> Row1[Строка: Масло]
    Pancakes --> Row2[Строка: Тесто]
    Row2 -->|sub_recipe| Dough[Рецепт: Тесто]
    Dough --> D1[Строка: Мука]
    Dough --> D2[Строка: Молоко]
    Dough --> D3[Строка: Яйца]
```

При расчете веса (брутто/нетто) или сериализации в JSON система рекурсивно обходит состав вложенного рецепта.

---

## 3. Общие связи моделей в хранилище

В `storage_manager` лежат списки объектов, которые ссылаются друг на друга:

```mermaid
graph TD
    Nomenclature[Номенклатура: Мука] -->|group| Group[Группа: Бакалея]
    Nomenclature -->|range| Range[Единица: Грамм]

    RecipeRow[Строка рецепта] -->|nomenclature| Nomenclature
    Recipe[Рецепт] -->|rows| RecipeRow
```

Конвертер `reference_convertor` находит эти ссылки через свойства (`@property`) и передает их в фабрику для формирования словарей.

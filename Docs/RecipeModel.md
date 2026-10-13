# UML-диаграмма: recipe_model и recipe_row_model

```mermaid
classDiagram
    direction TB

    class name_id {
        <<abstract>>
        -__name: str
        -__id: str
        +name: str
        +id: str
        +__eq__(other) bool
    }

    class recipe_model {
        -nomenclature_model __dish
        -list __rows
        -int __cooking_time
        -list __instructions
        -int __portions
        +dish: nomenclature_model
        +rows: list
        +cooking_time: int
        +instructions: list
        +portions: int
        +brutto: float
        +netto: float
        +add_row(row) bool
        +remove_row(row_or_id) bool
        +clear_rows() void
        +create_pancake_dough_recipe() recipe_model
        +create_pancakes_recipe() recipe_model
        +create_primary_list(nomenclatures) list
    }

    class recipe_row_model {
        -nomenclature_model __nomenclature
        -range_model __range
        -recipe_model __sub_recipe
        -float __brutto
        -float __netto
        +nomenclature: nomenclature_model
        +range: range_model
        +sub_recipe: recipe_model
        +brutto: float
        +netto: float
        +create_ingredient(nomenclature, brutto, netto) recipe_row_model
        +create_sub_recipe(nomenclature, sub_recipe, netto) recipe_row_model
    }

    class nomenclature_model {
        -__name: str
        -__group: nomenclature_group_model
        -__range: range_model
        +name: str
        +group: nomenclature_group_model
        +range: range_model
    }

    class range_model {
        -__name: str
        +name: str
    }

    name_id <|-- recipe_model
    name_id <|-- recipe_row_model
    name_id <|-- nomenclature_model
    name_id <|-- range_model

    recipe_model "1" *-- "*" recipe_row_model : rows
    recipe_model o-- nomenclature_model : dish
    recipe_row_model o-- nomenclature_model : nomenclature
    recipe_row_model o-- range_model : range
    recipe_row_model "0..1" o-- "1" recipe_model : sub_recipe
```

## Описание доменной модели

### 1. Сущности
* **`recipe_model`** — технологическая карта блюда или полуфабриката. Содержит наименование блюда (`dish`), список строк (`rows`), время приготовления (`cooking_time`), инструкцию (`instructions`) и количество порций (`portions`).
* **`recipe_row_model`** — строка технологической карты. Описывает использование ингредиента (`nomenclature`) или полуфабриката (`sub_recipe`).

### 2. Паттерны и связи
* **Композиция (`recipe_model *-- recipe_row_model`):** строки рецепта принадлежат конкретной технологической карте и не существуют отдельно от нее.
* **Рекурсивная агрегация (`recipe_row_model o-- recipe_model`):** строка может ссылаться на другую технологическую карту (`sub_recipe`), что позволяет строить иерархические рецепты с полуфабрикатами произвольной глубины.
* **Фабричные методы (Factory Method):** инкапсулируют создание строк (`create_ingredient`, `create_sub_recipe`) и готовых технологических карт (`create_pancake_dough_recipe`, `create_pancakes_recipe`, `create_primary_list`).

### 3. Расчет массы (на 1 порцию)
* Массы `brutto` и `netto` в `recipe_model` вычисляются динамически суммированием строк.
* Для полуфабрикатов масса `brutto` рассчитывается рекурсивно из `sub_recipe.brutto`.

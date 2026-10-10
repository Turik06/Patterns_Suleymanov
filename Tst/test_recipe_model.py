import pytest
from Src.Core.exception import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.recipe_model import recipe_model


@pytest.fixture
def sample_data():
    """Фикстура базовых сущностей для тестирования рецептов."""
    grocery = nomenclature_group_model.create_grocery()
    dairy = nomenclature_group_model.create_dairy()
    dishes = nomenclature_group_model.create_dishes()

    kg = range_model.create_kilogram()
    piece = range_model.create_piece()

    flour = nomenclature_model.create_flour(grocery, kg)
    milk = nomenclature_model.create_milk(dairy, kg)
    eggs = nomenclature_model.create_eggs(dairy, piece)
    butter = nomenclature_model.create_butter(dairy, kg)
    sugar = nomenclature_model.create_sugar(grocery, kg)
    salt = nomenclature_model.create_salt(grocery, kg)

    dough = nomenclature_model.create_pancake_dough(dishes, piece)
    pancakes = nomenclature_model.create_pancakes(dishes, piece)

    return {
        "flour": flour,
        "milk": milk,
        "eggs": eggs,
        "butter": butter,
        "sugar": sugar,
        "salt": salt,
        "dough": dough,
        "pancakes": pancakes,
    }


# ==================== Тесты recipe_row_model ====================


def test_success_recipe_row_create_ingredient(sample_data):
    """
    Ожидание: Корректное создание строки обычного ингредиента с заданными весами.
    Метод: recipe_row_model.create_ingredient
    Описание: Проверяет установку наименования, номенклатуры, брутто и нетто.
    """
    # Arrange & Act
    row = recipe_row_model.create_ingredient(sample_data["flour"], brutto=50.0, netto=48.0)

    # Assert
    assert row.name == "Мука пшеничная"
    assert row.nomenclature == sample_data["flour"]
    assert row.brutto == 50.0
    assert row.netto == 48.0
    assert row.sub_recipe is None


def test_success_recipe_row_default_netto(sample_data):
    """
    Ожидание: Если нетто не передано, оно приравнивается к брутто.
    Метод: recipe_row_model.create_ingredient
    Описание: Проверяет дефолтное равенство нетто и брутто.
    """
    # Arrange & Act
    row = recipe_row_model.create_ingredient(sample_data["sugar"], brutto=7.5)

    # Assert
    assert row.brutto == 7.5
    assert row.netto == 7.5


def test_error_recipe_row_negative_weights(sample_data):
    """
    Ожидание: Исключение argument_exception при отрицательном весе брутто или нетто.
    Метод: recipe_row_model.brutto / netto setters
    Описание: Вес ингредиента не может быть отрицательным числом.
    """
    # Arrange
    row = recipe_row_model.create_ingredient(sample_data["flour"], brutto=10.0)

    # Act & Assert
    with pytest.raises(argument_exception):
        row.brutto = -5.0

    with pytest.raises(argument_exception):
        row.netto = -1.0


# ==================== Тесты recipe_model ====================


def test_success_recipe_model_create(sample_data):
    """
    Ожидание: Создание модели рецепта со всеми атрибутами.
    Метод: recipe_model.__init__
    Описание: Проверяет установку названия, целевого блюда, порций и времени.
    """
    # Arrange & Act
    recipe = recipe_model(
        name="Тесто",
        dish=sample_data["dough"],
        cooking_time=15,
        instructions=["Шаг 1", "Шаг 2"],
        portions=1
    )

    # Assert
    assert recipe.name == "Тесто"
    assert recipe.dish == sample_data["dough"]
    assert recipe.cooking_time == 15
    assert recipe.portions == 1
    assert len(recipe.instructions) == 2
    assert len(recipe.rows) == 0


def test_success_recipe_brutto_netto_calculation(sample_data):
    """
    Ожидание: Брутто и нетто рецепта равны сумме весов всех строк.
    Метод: recipe_model.brutto / netto
    Описание: Проверяет сложение веса каждого ингредиента.
    """
    # Arrange
    recipe = recipe_model(name="Тесто", dish=sample_data["dough"])
    r1 = recipe_row_model.create_ingredient(sample_data["flour"], brutto=50.0, netto=50.0)
    r2 = recipe_row_model.create_ingredient(sample_data["milk"], brutto=125.0, netto=125.0)
    r3 = recipe_row_model.create_ingredient(sample_data["eggs"], brutto=25.0, netto=22.0)

    # Act
    recipe.add_row(r1)
    recipe.add_row(r2)
    recipe.add_row(r3)

    # Assert
    assert recipe.brutto == 200.0   # 50 + 125 + 25
    assert recipe.netto == 197.0    # 50 + 125 + 22


def test_success_recipe_dynamic_recalculation_on_add_and_remove(sample_data):
    """
    Ожидание: Брутто и нетто автоматически пересчитываются при добавлении и удалении ингредиента.
    Метод: recipe_model.add_row / remove_row
    Описание: Проверяет динамический пересчет и удаление как по объекту, так и по строковому id.
    """
    # Arrange
    recipe = recipe_model(name="Тесто", dish=sample_data["dough"])
    r1 = recipe_row_model.create_ingredient(sample_data["flour"], brutto=50.0, netto=50.0)
    r2 = recipe_row_model.create_ingredient(sample_data["sugar"], brutto=10.0, netto=10.0)
    recipe.add_row(r1)

    assert recipe.brutto == 50.0

    # Act 1: Добавление нового ингредиента
    recipe.add_row(r2)

    # Assert 1: Вес увеличился
    assert recipe.brutto == 60.0
    assert recipe.netto == 60.0

    # Act 2: Удаление ингредиента по объекту
    res1 = recipe.remove_row(r2)

    # Assert 2: Вес уменьшился обратно
    assert res1 is True
    assert recipe.brutto == 50.0

    # Act 3: Удаление по строковому id
    res2 = recipe.remove_row(r1.id)

    # Assert 3: Список пуст, вес равен нулю
    assert res2 is True
    assert recipe.brutto == 0.0
    assert recipe.netto == 0.0


def test_success_recipe_recursive_semi_finished_calculation(sample_data):
    """
    Ожидание: Рекурсивный расчёт брутто и нетто для рецепта с полуфабрикатом.
    Метод: recipe_model.brutto / netto с sub_recipe
    Описание: Блюдо 'Блины' включает полуфабрикат 'Тесто' и масло. Брутто теста
              вычисляется рекурсивно из его сырья, а нетто учитывает упек при жарке.
    """
    # Arrange: 1. Создаем рецепт полуфабриката (Тесто)
    dough_recipe = recipe_model.create_pancake_dough_recipe(
        dough_dish=sample_data["dough"],
        flour=sample_data["flour"],
        milk=sample_data["milk"],
        eggs=sample_data["eggs"],
        sugar=sample_data["sugar"],
        salt=sample_data["salt"],
    )
    # 50 + 125 + 25 + 7.5 + 1.25 = 208.75 брутто
    # 50 + 125 + 22 + 7.5 + 1.25 = 205.75 нетто
    assert dough_recipe.brutto == 208.75
    assert dough_recipe.netto == 205.75

    # Arrange: 2. Создаем готовое блюдо (Блины) с полуфабрикатом теста и маслом
    pancakes_recipe = recipe_model.create_pancakes_recipe(
        pancakes_dish=sample_data["pancakes"],
        dough_dish=sample_data["dough"],
        dough_recipe=dough_recipe,
        butter=sample_data["butter"],
    )

    # Act & Assert
    # Брутто блинов = брутто теста (рекурсивно 208.75) + масло (12.5) = 221.25
    assert pancakes_recipe.brutto == 221.25
    # Нетто блинов = нетто жареных блинов (175.0) + масло (12.5) = 187.5
    assert pancakes_recipe.netto == 187.5


def test_error_recipe_model_invalid_arguments(sample_data):
    """
    Ожидание: Исключения при передаче некорректных типов в рецепт.
    Метод: recipe_model.add_row / portions / cooking_time setters
    Описание: Проверяет валидацию порций (>0), времени готовки (>=0) и строки рецепта.
    """
    recipe = recipe_model(name="Тест", dish=sample_data["dough"])

    with pytest.raises(argument_exception):
        recipe.add_row("не строка рецепта")

    with pytest.raises(argument_exception):
        recipe.portions = 0

    with pytest.raises(argument_exception):
        recipe.cooking_time = -10


def test_success_recipe_dish_in_dish_recursion(sample_data):
    """
    Ожидание: Прямое добавление блюда в блюдо (recipe_model в add_row) и корректный рекурсивный расчёт веса.
    Метод: recipe_model.add_row / brutto / netto
    Описание: Проверяет вариант 'блюдо в блюде': добавление объекта recipe_model как полуфабриката
              и многоуровневый рекурсивный пересчет брутто и нетто.
    """
    # Arrange: 1. Базовый рецепт теста (полуфабрикат)
    dough = recipe_model(name="Тесто", dish=sample_data["dough"])
    dough.add_row(recipe_row_model.create_ingredient(sample_data["flour"], brutto=50.0, netto=50.0))
    dough.add_row(recipe_row_model.create_ingredient(sample_data["milk"], brutto=100.0, netto=100.0))

    # Arrange: 2. Блюдо "Блины", куда добавляем тесто напрямую (вариант "блюдо в блюде")
    pancakes = recipe_model(name="Блины", dish=sample_data["pancakes"])
    pancakes.add_row(dough)  # Передаем recipe_model напрямую
    pancakes.add_row(recipe_row_model.create_ingredient(sample_data["butter"], brutto=10.0, netto=10.0))

    # Assert: 2. Проверяем рекурсивный вес "Блинов"
    assert len(pancakes.rows) == 2
    assert pancakes.brutto == 160.0  # 150 (из вложенного рецепта) + 10
    assert pancakes.netto == 160.0   # 150 + 10

    # Arrange: 3. Третий уровень вложенности: "Сет блинный" включает готовые "Блины"
    combo_set = recipe_model(name="Сет блинный", dish=sample_data["pancakes"])
    combo_set.add_row(pancakes)  # Блюдо в блюде второго уровня вложенности

    # Assert: 3. Глубокая рекурсия работает через все уровни
    assert combo_set.brutto == 160.0
    assert combo_set.netto == 160.0

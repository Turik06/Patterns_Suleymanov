from Src.Core.abstract_model import name_id
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_row_model import recipe_row_model


class recipe_model(name_id):
    """
    Модель рецепта (технологической карты).
    """

    def __init__(
        self,
        name: str = "",
        dish: nomenclature_model = None,
        cooking_time: int = 0,
        instructions: list = None,
        portions: int = 1
    ):
        super().__init__()
        self.__dish = dish
        self.__rows = []
        self.__cooking_time = cooking_time
        self.__instructions = instructions or []
        self.__portions = portions

        if name:
            self.name = name

    @property
    def dish(self) -> nomenclature_model:
        return self.__dish

    @dish.setter
    def dish(self, value: nomenclature_model):
        validator.validate(value, nomenclature_model)
        self.__dish = value

    @property
    def rows(self) -> list:
        return self.__rows

    @property
    def cooking_time(self) -> int:
        return self.__cooking_time

    @cooking_time.setter
    def cooking_time(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise argument_exception("cooking_time", "Время приготовления должно быть неотрицательным")
        self.__cooking_time = value

    @property
    def instructions(self) -> list:
        return self.__instructions

    @instructions.setter
    def instructions(self, value: list):
        validator.validate(value, list)
        self.__instructions = value

    @property
    def portions(self) -> int:
        return self.__portions

    @portions.setter
    def portions(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise argument_exception("portions", "Количество порций должно быть больше нуля")
        self.__portions = value

    @property
    def brutto(self) -> float:
        """Суммарный вес брутто (в граммах)."""
        return round(sum(row.brutto for row in self.__rows), 2)

    @property
    def netto(self) -> float:
        """Суммарный вес нетто (в граммах)."""
        return round(sum(row.netto for row in self.__rows), 2)

    def add_row(self, row: recipe_row_model) -> bool:
        """Добавить строку в рецепт."""
        validator.validate(row, recipe_row_model)
        self.__rows.append(row)
        return True

    def remove_row(self, row_or_id) -> bool:
        """Удалить строку по объекту или по id (без каскада if)."""
        target_id = getattr(row_or_id, "id", str(row_or_id))
        initial_len = len(self.__rows)
        self.__rows = [row for row in self.__rows if row.id != target_id]
        return len(self.__rows) < initial_len

    def clear_rows(self) -> None:
        self.__rows.clear()

    @staticmethod
    def create_pancake_dough_recipe(
        dough_dish: nomenclature_model,
        flour: nomenclature_model,
        milk: nomenclature_model,
        eggs: nomenclature_model,
        sugar: nomenclature_model,
        salt: nomenclature_model,
    ):
        """
        Фабричный метод: Технологическая карта полуфабриката 'Тесто для блинов' (на 1 порцию).
        """
        recipe = recipe_model(
            name="Тесто для блинов",
            dish=dough_dish,
            cooking_time=15,
            instructions=[
                "В глубокую емкость разбить яйца, добавить сахар и соль, взбить венчиком.",
                "Влить теплое молоко (около 30°C), перемешать.",
                "Постепенно ввести просеянную муку, вымешивая венчиком до однородного жидкого теста.",
            ],
            portions=1,
        )
        recipe.add_row(recipe_row_model.create_ingredient(flour, brutto=50.0, netto=50.0))
        recipe.add_row(recipe_row_model.create_ingredient(milk, brutto=125.0, netto=125.0))
        recipe.add_row(recipe_row_model.create_ingredient(eggs, brutto=25.0, netto=22.0))
        recipe.add_row(recipe_row_model.create_ingredient(sugar, brutto=7.5, netto=7.5))
        recipe.add_row(recipe_row_model.create_ingredient(salt, brutto=1.25, netto=1.25))
        return recipe

    @staticmethod
    def create_pancakes_recipe(
        pancakes_dish: nomenclature_model,
        dough_dish: nomenclature_model,
        dough_recipe,
        butter: nomenclature_model,
    ):
        """
        Фабричный метод: Технологическая карта блюда 'Блины классические' (на 1 порцию).
        Включает полуфабрикат 'Тесто для блинов' и сливочное масло.
        """
        recipe = recipe_model(
            name="Блины классические",
            dish=pancakes_dish,
            cooking_time=25,
            instructions=[
                "Разогреть блинную сковороду до 180-200°C и смазать тонким слоем масла.",
                "Половником налить порцию теста и равномерно распределить по сковороде.",
                "Выпекать 60-80 секунд с одной стороны и 30-40 секунд с обратной.",
                "Готовый блин переложить на блюдо и смазать сливочным маслом.",
            ],
            portions=1,
        )
        recipe.add_row(recipe_row_model.create_sub_recipe(dough_dish, sub_recipe=dough_recipe, netto=175.0))
        recipe.add_row(recipe_row_model.create_ingredient(butter, brutto=12.5, netto=12.5))
        return recipe

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

from Src.Core.abstract_model import name_id
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class recipe_row_model(name_id):
    """
    Строка технологической карты (ингредиент, полуфабрикат или упаковка).
    """

    def __init__(
        self,
        nomenclature: nomenclature_model = None,
        brutto: float = 0.0,
        netto: float = 0.0,
        range_unit: range_model = None,
        sub_recipe = None,
    ):
        super().__init__()
        self.__nomenclature = nomenclature
        self.__range = range_unit or getattr(nomenclature, "range", None)
        self.__sub_recipe = sub_recipe
        self.__brutto = float(brutto)
        self.__netto = float(netto or brutto)

        if nomenclature and getattr(nomenclature, "name", None):
            self.name = nomenclature.name

    @property
    def nomenclature(self) -> nomenclature_model:
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model):
        validator.validate(value, nomenclature_model)
        self.__nomenclature = value

    @property
    def range(self) -> range_model:
        return self.__range

    @range.setter
    def range(self, value: range_model):
        validator.validate(value, range_model)
        self.__range = value

    @property
    def sub_recipe(self):
        return self.__sub_recipe

    @sub_recipe.setter
    def sub_recipe(self, value):
        if value is not None and not hasattr(value, "brutto"):
            raise argument_exception("sub_recipe", "Вложенный рецепт должен иметь свойство brutto")
        self.__sub_recipe = value

    @property
    def brutto(self) -> float:
        """Брутто: рекурсивно из полуфабриката или собственный вес."""
        return self.__sub_recipe.brutto if self.__sub_recipe else self.__brutto

    @brutto.setter
    def brutto(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise argument_exception("brutto", "Масса брутто должна быть неотрицательным числом")
        self.__brutto = float(value)

    @property
    def netto(self) -> float:
        """Нетто: заданный вес или рекурсивно из полуфабриката."""
        return self.__netto if self.__netto > 0 else (self.__sub_recipe.netto if self.__sub_recipe else self.__brutto)

    @netto.setter
    def netto(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise argument_exception("netto", "Масса нетто должна быть неотрицательным числом")
        self.__netto = float(value)

    # Фабричные методы
    @staticmethod
    def create_ingredient(nomenclature: nomenclature_model, brutto: float, netto: float = None):
        """Фабричный метод для создания обычного ингредиента."""
        return recipe_row_model(nomenclature=nomenclature, brutto=brutto, netto=netto)

    @staticmethod
    def create_sub_recipe(nomenclature: nomenclature_model, sub_recipe, netto: float = None):
        """Фабричный метод для создания строки с полуфабрикатом."""
        return recipe_row_model(nomenclature=nomenclature, sub_recipe=sub_recipe, netto=netto)

from Src.Models.recipe_model import recipe_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto


"""
DTO рецепта
"""
class recipe_dto(abstract_dto):
    __unique_code: str = ""
    __name: str = ""
    __items: list = None
    __brutto: float = 0.0
    __netto: float = 0.0
    __instructions: list = None

    def __init__(self):
        self.__items = []
        self.__instructions = []

    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        validator.validate(value, str)
        self.__unique_code = value.strip()

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        validator.validate(value, str)
        self.__name = value.strip()

    @property
    def items(self) -> list:
        return self.__items

    @items.setter
    def items(self, value: list) -> None:
        validator.validate(value, list)
        self.__items = value

    @property
    def brutto(self) -> float:
        return self.__brutto

    @brutto.setter
    def brutto(self, value: float) -> None:
        validator.validate(value, (int, float))
        self.__brutto = float(value)

    @property
    def netto(self) -> float:
        return self.__netto

    @netto.setter
    def netto(self, value: float) -> None:
        validator.validate(value, (int, float))
        self.__netto = float(value)

    @property
    def instructions(self) -> list:
        return self.__instructions

    @instructions.setter
    def instructions(self, value: list) -> None:
        validator.validate(value, list)
        self.__instructions = value

    def from_domain_model(self, source: recipe_model) -> "recipe_dto":
        validator.validate(source, recipe_model)

        dto = recipe_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.brutto = source.brutto
        dto.netto = source.netto
        dto.instructions = list(source.instructions)
        dto.items = [item.unique_code for item in source.items]
        return dto

    def to_domain_model(self, cache: dict = None) -> recipe_model:
        model = recipe_model(self.name)
        model.instructions = list(self.instructions)
        if cache and self.items:
            for item_code in self.items:
                if item_code in cache:
                    model.add_row(cache[item_code])
        if self.unique_code:
            model.unique_code = self.unique_code
        return model

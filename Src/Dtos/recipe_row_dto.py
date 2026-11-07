from Src.Models.recipe_row_model import recipe_row_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto


"""
DTO строки рецепта
"""
class recipe_row_dto(abstract_dto):
    __unique_code: str = ""
    __name: str = ""
    __nomenclature_code: str = ""
    __range_code: str = ""
    __brutto: float = 0.0
    __netto: float = 0.0

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
    def nomenclature_code(self) -> str:
        return self.__nomenclature_code

    @nomenclature_code.setter
    def nomenclature_code(self, value: str) -> None:
        validator.validate(value, str)
        self.__nomenclature_code = value.strip()

    @property
    def range_code(self) -> str:
        return self.__range_code

    @range_code.setter
    def range_code(self, value: str) -> None:
        validator.validate(value, str)
        self.__range_code = value.strip()

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

    def from_domain_model(self, source: recipe_row_model) -> "recipe_row_dto":
        validator.validate(source, recipe_row_model)

        dto = recipe_row_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.brutto = source.brutto
        dto.netto = source.netto
        if source.nomenclature is not None:
            dto.nomenclature_code = source.nomenclature.unique_code
        if source.range is not None:
            dto.range_code = source.range.unique_code

        return dto

    def to_domain_model(self, cache: dict = None) -> recipe_row_model:
        nom = cache.get(self.nomenclature_code) if cache else None
        range_unit = cache.get(self.range_code) if cache else None
        model = recipe_row_model(nom, self.brutto, self.netto, range_unit)
        if self.unique_code:
            model.unique_code = self.unique_code
        return model

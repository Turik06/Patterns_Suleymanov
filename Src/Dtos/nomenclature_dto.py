from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto


"""
DTO номенклатуры
"""
class nomenclature_dto(abstract_dto):
    __unique_code: str = ""
    __name: str = ""
    __group_code: str = ""
    __range_code: str = ""

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
    def group_code(self) -> str:
        return self.__group_code

    @group_code.setter
    def group_code(self, value: str) -> None:
        validator.validate(value, str)
        self.__group_code = value.strip()

    @property
    def range_code(self) -> str:
        return self.__range_code

    @range_code.setter
    def range_code(self, value: str) -> None:
        validator.validate(value, str)
        self.__range_code = value.strip()

    def from_domain_model(self, source: nomenclature_model) -> "nomenclature_dto":
        validator.validate(source, nomenclature_model)

        dto = nomenclature_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        if source.group is not None:
            dto.group_code = source.group.unique_code
        if source.range is not None:
            dto.range_code = source.range.unique_code

        return dto

    def to_domain_model(self, cache: dict = None) -> nomenclature_model:
        group = cache.get(self.group_code) if cache else None
        range_unit = cache.get(self.range_code) if cache else None
        model = nomenclature_model(self.name, self.name, group, range_unit)
        if self.unique_code:
            model.unique_code = self.unique_code
        return model

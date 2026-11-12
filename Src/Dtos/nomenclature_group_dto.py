from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto


"""
DTO группы номенклатуры
"""
class nomenclature_group_dto(abstract_dto):
    __unique_code: str = ""
    __name: str = ""

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

    def from_domain_model(self, source: nomenclature_group_model) -> "nomenclature_group_dto":
        validator.validate(source, nomenclature_group_model)

        dto = nomenclature_group_dto()
        dto.type = getattr(source, "type", source.__class__.__name__)
        dto.unique_code = source.unique_code
        dto.name = source.name
        return dto


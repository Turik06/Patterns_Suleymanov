from Src.Models.range_model import range_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto


"""
DTO единицы измерения
"""
class range_dto(abstract_dto):
    __unique_code: str = ""
    __name: str = ""
    __value: int = 1
    __base_code: str = ""

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
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, value: int) -> None:
        validator.validate(value, (int, float))
        self.__value = int(value)

    @property
    def base_code(self) -> str:
        return self.__base_code

    @base_code.setter
    def base_code(self, value: str) -> None:
        validator.validate(value, str)
        self.__base_code = value.strip()

    def from_domain_model(self, source: range_model) -> "range_dto":
        validator.validate(source, range_model)

        dto = range_dto()
        dto.type = getattr(source, "type", source.__class__.__name__)
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.value = source.value
        if source.base is not None:
            dto.base_code = source.base.unique_code

        return dto


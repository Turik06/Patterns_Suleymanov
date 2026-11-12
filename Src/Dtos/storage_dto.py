from Src.Models.storage_model import storage_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto


"""
DTO склада
"""
class storage_dto(abstract_dto):
    __unique_code: str = ""
    __name: str = ""
    __address: str = ""

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
    def address(self) -> str:
        return self.__address

    @address.setter
    def address(self, value: str) -> None:
        validator.validate(value, str)
        self.__address = value.strip()

    def from_domain_model(self, source: storage_model) -> "storage_dto":
        validator.validate(source, storage_model)

        dto = storage_dto()
        dto.type = getattr(source, "type", source.__class__.__name__)
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.address = source.address
        return dto


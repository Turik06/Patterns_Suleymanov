from Src.Models.organization_model import organization_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto


"""
DTO организации
"""
class company_dto(abstract_dto):
    __unique_code: str = ""
    __name: str = ""
    __inn: str = ""
    __bik: str = ""

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
    def inn(self) -> str:
        return self.__inn

    @inn.setter
    def inn(self, value: str) -> None:
        validator.validate(value, str)
        self.__inn = value.strip()

    @property
    def bik(self) -> str:
        return self.__bik

    @bik.setter
    def bik(self, value: str) -> None:
        validator.validate(value, str)
        self.__bik = value.strip()

    def from_domain_model(self, source: organization_model) -> "company_dto":
        validator.validate(source, organization_model)

        dto = company_dto()
        dto.type = getattr(source, "type", source.__class__.__name__)
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.inn = source.inn
        dto.bik = source.bik
        return dto


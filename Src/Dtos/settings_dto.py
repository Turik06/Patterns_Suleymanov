from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Dtos.company_dto import company_dto
from Src.Models.settings_model import settings_model


class settings_dto(abstract_dto):
    """DTO настроек приложения"""
    __boss_name: str = ""
    __account_name: str = ""
    __is_first_start: bool = False
    __response_format: str = "html"
    __organization: company_dto = None

    @property
    def boss_name(self) -> str:
        """Имя руководителя"""
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        """Задать имя руководителя"""
        validator.validate(value, str)
        self.__boss_name = value.strip()

    @property
    def account_name(self) -> str:
        """Имя бухгалтера"""
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str) -> None:
        """Задать имя бухгалтера"""
        validator.validate(value, str)
        self.__account_name = value.strip()

    @property
    def is_first_start(self) -> bool:
        """Первый старт"""
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        """Задать флаг первого старта"""
        validator.validate(value, bool)
        self.__is_first_start = value

    @property
    def first_start(self) -> bool:
        """Первый старт (синоним)"""
        return self.__is_first_start

    @first_start.setter
    def first_start(self, value: bool) -> None:
        """Задать флаг первого старта"""
        validator.validate(value, bool)
        self.__is_first_start = value

    @property
    def response_format(self) -> str:
        """Формат ответа"""
        return self.__response_format

    @response_format.setter
    def response_format(self, value: str) -> None:
        """Задать формат ответа"""
        self.__response_format = str(value)

    @property
    def organization(self) -> company_dto:
        """DTO организации"""
        return self.__organization

    @organization.setter
    def organization(self, value) -> None:
        """Задать организацию"""
        if isinstance(value, dict):
            from Src.Logics.convertor import convertor
            self.__organization = convertor().resolve_dto(value, type_hint="organization")
        elif isinstance(value, company_dto):
            self.__organization = value

    @property
    def company(self) -> company_dto:
        """Организация (синоним)"""
        return self.__organization

    @company.setter
    def company(self, value) -> None:
        """Задать организацию"""
        self.organization = value

    @property
    def company_name(self) -> str:
        """Название организации (плоский формат)"""
        return self.__organization.name if self.__organization else ""

    @company_name.setter
    def company_name(self, value: str) -> None:
        """Задать название организации (плоский формат)"""
        if not self.__organization:
            self.__organization = company_dto()
        self.__organization.name = value

    def load_dict(self, data: dict):
        """Загрузить данные из словаря"""
        super().load_dict(data)
        if "company_name" in data and not self.__organization:
            dto = company_dto()
            dto.name = data["company_name"]
            self.__organization = dto
        return self

    def from_domain_model(self, source: settings_model) -> "settings_dto":
        """Создать DTO из модели настроек"""
        validator.validate(source, settings_model)
        dto = settings_dto()
        dto.boss_name = source.boss_name
        dto.account_name = source.account_name
        dto.is_first_start = source.is_first_start
        dto.response_format = source.response_format.name if hasattr(source.response_format, "name") else str(source.response_format)
        if source.organization:
            dto.organization = company_dto().from_domain_model(source.organization)
        return dto

from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator
from Src.Core.exception import argument_exception
from Src.Models.organization_model import organization_model
from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.response_format_dto import response_format_dto
from Src.Core.event_type import event_type
from Src.Logics.observer import observer


class settings_model(abstract_model):
    """Модель настроек приложения."""

    # Карточка организации
    __organization: organization_model = None
    # Наименование руководителя
    __boss_name: str = ""
    # Наименование главного бухгалтера
    __account_name: str = ""
    # Флаг первого старта приложения
    __is_first_start: bool = False
    # Формат ответа по умолчанию
    __response_format: report_type_enum = report_type_enum.HTML

    @property
    def organization(self) -> organization_model:
        """Карточка организации."""
        return self.__organization

    @organization.setter
    def organization(self, value: organization_model) -> None:
        """Задаёт карточку организации."""
        validator.validate(value, organization_model)
        if self.__organization != value:
            self.__organization = value
            observer.create(event_type.change_settings(), {"field": "organization", "value": getattr(value, "name", "")})

    @property
    def company(self) -> organization_model:
        """Псевдоним для карточки организации."""
        return self.__organization

    @company.setter
    def company(self, value: organization_model) -> None:
        """Задаёт карточку организации (псевдоним)."""
        self.organization = value

    @property
    def boss_name(self) -> str:
        """Наименование руководителя."""
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        """Задаёт наименование руководителя."""
        validator.validate(value, str, 255)
        clean = value.strip()
        if self.__boss_name != clean:
            self.__boss_name = clean
            observer.create(event_type.change_settings(), {"field": "boss_name", "value": clean})

    @property
    def account_name(self) -> str:
        """Наименование главного бухгалтера."""
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str) -> None:
        """Задаёт наименование главного бухгалтера."""
        validator.validate(value, str, 255)
        clean = value.strip()
        if self.__account_name != clean:
            self.__account_name = clean
            observer.create(event_type.change_settings(), {"field": "account_name", "value": clean})

    @property
    def is_first_start(self) -> bool:
        """Флаг первого старта приложения."""
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        """Задаёт флаг первого старта приложения."""
        validator.validate(value, bool)
        if self.__is_first_start != value:
            self.__is_first_start = value
            observer.create(event_type.change_settings(), {"field": "is_first_start", "value": value})

    @property
    def first_start(self) -> bool:
        """Флаг первого старта (псевдоним для is_first_start)."""
        return self.__is_first_start

    @first_start.setter
    def first_start(self, value: bool) -> None:
        """Задаёт флаг первого старта (псевдоним для is_first_start)."""
        validator.validate(value, bool)
        if self.__is_first_start != value:
            self.__is_first_start = value
            observer.create(event_type.change_settings(), {"field": "is_first_start", "value": value})

    @property
    def response_format(self) -> report_type_enum:
        """Формат ответа по умолчанию."""
        return self.__response_format

    @response_format.setter
    def response_format(self, value) -> None:
        """Задаёт формат ответа по умолчанию."""
        from Src.Logics.settings_manager import settings_manager
        new_format = settings_manager.convert_report_type(value)
        if self.__response_format != new_format:
            self.__response_format = new_format
            observer.create(event_type.change_settings(), {"field": "response_format", "value": new_format.name})

    @staticmethod
    def from_dto(dto, resolver=None):
        """Создать модель из DTO"""
        result = settings_model()
        if hasattr(dto, "boss_name") and dto.boss_name:
            result.boss_name = dto.boss_name
        if hasattr(dto, "account_name") and dto.account_name:
            result.account_name = dto.account_name
        if hasattr(dto, "is_first_start"):
            result.is_first_start = dto.is_first_start
        if hasattr(dto, "response_format") and dto.response_format:
            result.response_format = dto.response_format
        if hasattr(dto, "organization") and dto.organization:
            if isinstance(dto.organization, organization_model):
                result.organization = dto.organization
            else:
                from Src.Logics.mapping_factory import mapping_factory
                result.organization = mapping_factory().to_model(dto.organization, resolver)
        return result
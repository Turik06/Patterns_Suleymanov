from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator
from Src.Models.organization_model import organization_model


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

    @property
    def organization(self) -> organization_model:
        """Карточка организации."""
        return self.__organization

    @organization.setter
    def organization(self, value: organization_model) -> None:
        """Задаёт карточку организации."""
        validator.validate(value, organization_model)
        self.__organization = value

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
        self.__boss_name = value.strip()

    @property
    def account_name(self) -> str:
        """Наименование главного бухгалтера."""
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str) -> None:
        """Задаёт наименование главного бухгалтера."""
        validator.validate(value, str, 255)
        self.__account_name = value.strip()

    @property
    def is_first_start(self) -> bool:
        """Флаг первого старта приложения."""
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        """Задаёт флаг первого старта приложения."""
        validator.validate(value, bool)
        self.__is_first_start = value

    @property
    def first_start(self) -> bool:
        """Флаг первого старта (псевдоним для is_first_start)."""
        return self.__is_first_start

    @first_start.setter
    def first_start(self, value: bool) -> None:
        """Задаёт флаг первого старта (псевдоним для is_first_start)."""
        validator.validate(value, bool)
        self.__is_first_start = value
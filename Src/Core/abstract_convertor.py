from abc import ABC, abstractmethod
from typing import Any
from Src.Core.validator import validator

_UNSET = object()


"""
Абстрактный конвертор
"""
class abstract_convertor(ABC):
    __error_text: str = ""

    """
    Текст ошибки
    """
    @property
    def error_text(self) -> str:
        return self.__error_text

    @error_text.setter
    def error_text(self, value: str) -> None:
        validator.validate(value, str)
        self.__error_text = value.strip()

    """
    Записать ошибку
    """
    def set_exception(self, ex: Exception) -> None:
        self.__error_text = f"Ошибка! Исключение {ex}"

    """
    Сериализация в словарь
    """
    def serialize(self, field: str, object: any) -> dict:
        validator.validate(field, str)
        return self.convert(field, object)

    """
    Десериализация из словаря
    """
    def deserialize(self, source: dict) -> object:
        pass

    """
    Конвертация в словарь
    """
    @abstractmethod
    def convert(self, field: Any, obj: Any = _UNSET) -> dict:
        pass


abstract_covertor = abstract_convertor

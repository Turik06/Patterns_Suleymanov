from abc import ABC, abstractmethod
from typing import Any
from Src.Core.exception import argument_exception


_UNSET = object()


class abstract_convertor(ABC):
    """
    Абстрактный базовый класс конвертера данных в словарь.
    """

    @abstractmethod
    def convert(self, field: Any, obj: Any = _UNSET) -> dict:
        """
        Преобразовать переданный объект в словарь.

        Параметры:
            field: Наименование поля (ключ результирующего словаря) или исходный объект
            obj: Исходный объект данных любого типа (если передан field)

        Возвращает:
            dict: Словарь формата {field: converted_data} или словарь свойств объекта
        """
        pass

    def Convert(self, field: Any, obj: Any = _UNSET) -> dict:
        """
        Алиас метода convert с заглавной буквы (для строгой совместимости с формулировкой ТЗ).
        """
        if obj is _UNSET:
            return self.convert(field)
        return self.convert(field, obj)


# Алиасы для совместимости с опечаткой в формулировке задания Forlabs и соглашениями об именовании
abstract_covertor = abstract_convertor
AbstractConvertor = abstract_convertor
AbstractCovertor = abstract_convertor

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


# Алиас для совместимости с опечаткой в формулировке задания Forlabs
abstract_covertor = abstract_convertor


from abc import ABC, abstractmethod
from typing import Any
from Src.Core.exception import argument_exception


class abstract_convertor(ABC):
    """
    Абстрактный базовый класс конвертера данных в словарь.
    """

    @abstractmethod
    def convert(self, field: str, obj: Any) -> dict:
        """
        Преобразовать переданный объект в словарь.

        Параметры:
            field: Наименование поля (ключ результирующего словаря)
            obj: Исходный объект данных любого типа

        Возвращает:
            dict: Словарь формата {field: converted_data}
        """
        pass

    def Convert(self, field: str, obj: Any) -> dict:
        """
        Алиас метода convert с заглавной буквы (для строгой совместимости с формулировкой ТЗ).
        """
        return self.convert(field, obj)


# Алиас для совместимости с опечаткой в формулировке задания Forlabs
abstract_covertor = abstract_convertor

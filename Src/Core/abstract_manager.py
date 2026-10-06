from abc import ABC
from Src.Core.validator import validator


"""
Абстрактный класс для реализации загрузки и обработки данных
"""
class abstract_manager(ABC):
    # Полный путь к файлу данных
    __file_name: str = ""
    # Флаг, указывающий, что данные загружены и обработаны
    _is_loaded: bool = False
    # Загруженные данные
    __data: list = []

    """
    Загружает данные из файла.
    """
    def load(self, file_name: str = "") -> None:
        pass

    """
    Обрабатывает загруженные данные.
    """
    def convert(self) -> bool:
        return self.build()

    """
    Обработать загруженные данные
    """
    def build(self) -> bool:
        return False

    """
    Флаг данные подготовленные
    """
    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @is_loaded.setter
    def is_loaded(self, value: bool) -> None:
        validator.validate(value, bool)
        self._is_loaded = value
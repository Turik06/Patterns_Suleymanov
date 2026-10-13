from abc import ABC
from Src.Core.validator import validator


class abstract_manager(ABC):
    """
    Абстрактный класс для реализации загрузки и обработки данных.
    """

    # Полный путь к файлу данных
    __file_name: str = ""
    # Флаг, указывающий, что данные загружены и обработаны
    _is_loaded: bool = False
    # Загруженные данные
    __data: list = []

    def load(self, file_name: str = "") -> None:
        """
        Загружает данные из файла.
        """
        pass

    def convert(self) -> bool:
        """
        Обрабатывает загруженные данные.
        """
        return self.build()

    def build(self) -> bool:
        """
        Обработать загруженные данные.
        """
        return False

    @property
    def is_loaded(self) -> bool:
        """
        Флаг, указывающий, подготовлены ли данные.
        """
        return self._is_loaded

    @is_loaded.setter
    def is_loaded(self, value: bool) -> None:
        """
        Устанавливает флаг готовности данных.
        """
        validator.validate(value, bool)
        self._is_loaded = value
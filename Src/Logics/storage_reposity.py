from Src.Core.abstract_model import abstact_model
from Src.Core.entity_model import entity_model
from Src.Core.validator import validator, operation_exception
from Src.Core.common import common


class storage_repository:
    """Репозиторий объектов и счетчиков ссылок"""

    __data: dict = {}
    __counts: dict = {}

    def __init__(self):
        self.__data = {}
        self.__counts = {}

    def registry(self, source: abstact_model):
        """Регистрация объекта и его вложений"""
        validator.validate(source, abstact_model)

        self.__data[source.unique_code] = source
        if source.unique_code in self.__counts:
            self.__counts[source.unique_code] += 1
        else:
            self.__counts[source.unique_code] = 0

        fields = common.get_fields(source, False)
        for field in fields:
            value = getattr(source, field)
            if isinstance(value, (abstact_model, entity_model)):
                self.registry(value)

    def registry_range(self, items: list):
        """Регистрация списка объектов"""
        validator.validate(items, list)
        for item in items:
            self.registry(item)

    def get(self, source: str):
        """Получить объект по коду"""
        validator.validate(source, str)
        if source in self.__data:
            return self.__data.get(source)
        raise operation_exception(f"Не найдена доменная сущность по коду : {source}!")

    def can_delete(self, source: abstact_model) -> bool:
        """Проверить, можно ли удалить объект"""
        validator.validate(source, abstact_model)
        try:
            self.get(source.unique_code)
            return self.__counts[source.unique_code] == 0
        except Exception:
            return False

    def delete(self, source: abstact_model):
        """Удалить объект из репозитория"""
        validator.validate(source, abstact_model)
        if not self.can_delete(source):
            raise operation_exception(f"Невозможно удалить запись {source.unique_code}!")

        self.__data.pop(source.unique_code, None)
        self.__counts.pop(source.unique_code, None)

    def clear(self):
        """Очистить репозиторий"""
        self.__data.clear()
        self.__counts.clear()

    @property
    def data(self) -> dict:
        """Словарь объектов"""
        return self.__data

    @property
    def counts(self) -> dict:
        """Счетчики ссылок"""
        return self.__counts

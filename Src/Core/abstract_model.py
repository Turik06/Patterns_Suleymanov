from abc import ABC
import uuid
from Src.Core.exception import argument_exception, max_length_exception


class name_id(ABC):
    """
    Абстрактный базовый класс для сущностей, обладающих наименованием и уникальным идентификатором.
    """

    # Максимальная длина наименования
    __max_name_length = 50

    def __init__(self):
        """
        Конструктор класса. Инициализирует имя пустой строкой и генерирует уникальный строковый id.
        """
        self.__name = ""
        self.__id = str(uuid.uuid4())

    @property
    def id(self):
        """
        Возвращает строковый идентификатор объекта.
        """
        if not hasattr(self, "_name_id__id") or not self._name_id__id:
            self._name_id__id = str(uuid.uuid4())
        return self._name_id__id

    @id.setter
    def id(self, value):
        """
        Задаёт строковый идентификатор объекта.
        """
        if value is not None and str(value).strip() != "":
            self._name_id__id = str(value).strip()
        else:
            raise argument_exception("id", "Идентификатор не должен быть пустым")

    @property
    def unique_code(self) -> str:
        """
        Возвращает уникальный код объекта (алиас для id / совместимость).
        """
        return self.id

    @unique_code.setter
    def unique_code(self, value: str):
        """
        Задаёт уникальный код объекта (алиас для id / совместимость).
        """
        self.id = value

    @property
    def name(self):
        """
        Возвращает наименование объекта.
        """
        if not hasattr(self, "_name_id__name"):
            self._name_id__name = ""
        return self._name_id__name

    @name.setter
    def name(self, new_name):
        """
        Задаёт наименование объекта. Максимальная длина — 50 символов.
        """
        if new_name is None or str(new_name).strip() == "":
            raise argument_exception("name", "Имя не должно быть пустым")

        value = str(new_name).strip()

        if len(value) > self.__max_name_length:
            raise max_length_exception("name", len(value), self.__max_name_length)

        self._name_id__name = value

    def __eq__(self, other):
        """
        Сравнение двух сущностей по их идентификатору.
        """
        if isinstance(other, name_id):
            return str(self.id) == str(other.id)
        return False

    def get_report_title(self) -> str:
        """Человекочитаемое наименование типа сущности."""
        return getattr(self, "__class__", type(self)).__name__

    def get_report_tag(self) -> str:
        """XML/HTML тег типа сущности."""
        return self.__class__.__name__.replace("_model", "").lower()

    def get_report_headers(self) -> list:
        """Заголовки колонок для отчета."""
        return ["Код", "Наименование"]

    def get_report_rows(self) -> list:
        """Строки данных для отчета."""
        return [[str(self.unique_code), str(self.name)]]

    def get_report_fields(self) -> dict:
        """Словарь полей (тег -> значение) для XML и структурированных представлений."""
        return {}

    def has_report_items(self) -> bool:
        """Флаг наличия вложенных табличных элементов."""
        return hasattr(self, "items") and bool(getattr(self, "items", None))

    def get_report_items(self) -> list:
        """Список вложенных элементов для детализированного отчета."""
        return list(getattr(self, "items", []))


abstract_model = name_id
abstact_model = name_id
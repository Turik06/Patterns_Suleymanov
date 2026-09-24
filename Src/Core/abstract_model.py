from abc import ABC
import uuid
from Src.Core.exception import argument_exception


class name_id(ABC):
    """
    Абстрактный базовый класс для сущностей, обладающих наименованием и уникальным идентификатором.
    """

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
        return self.__id

    @id.setter
    def id(self, value):
        """
        Задаёт строковый идентификатор объекта.
        """
        if value is not None and str(value).strip() != "":
            self.__id = str(value).strip()
        else:
            raise argument_exception("id", "Идентификатор не должен быть пустым")

    @property
    def name(self):
        """
        Возвращает наименование объекта.
        """
        return self.__name

    @name.setter
    def name(self, new_name):
        """
        Задаёт наименование объекта.
        """
        if new_name is not None and str(new_name).strip() != "":
            self.__name = str(new_name).strip()
        else:
            raise argument_exception("name", "Имя не должно быть пустым")

    def __eq__(self, other):
        """
        Сравнение двух сущностей по их идентификатору.
        """
        if isinstance(other, name_id):
            return str(self.id) == str(other.id)
        return False

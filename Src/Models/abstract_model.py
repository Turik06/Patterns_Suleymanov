from abc import ABC
import uuid


class name_id(ABC):
    """
    Абстрактный класс для имени и id объекта
    """

    def __init__(self):
        """Конструктор класса"""
        self.__name = ""
        self.__id = uuid.uuid4()

    @property
    def id(self):
        """Возвращает id объекта"""
        return self.__id

    @property
    def name(self) -> str:
        """Возвращает имя объекта"""
        return self.__name

    @name.setter
    def name(self, new_name: str):
        """Задаёт имя объекта"""
        if new_name is not None and len(new_name) > 0:
            self.__name = new_name
        else:
            raise ValueError("Имя не должно быть пустым")
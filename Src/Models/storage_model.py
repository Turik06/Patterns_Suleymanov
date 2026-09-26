from Src.Core.abstract_model import name_id
from Src.Core.exception import argument_exception


class storage_model(name_id):
    """
    Модель склада.
    Место хранения запасов продуктов и заготовок (например, "Основной склад", "Холодильник цеха").
    """

    def __init__(self, name="", address=""):
        """
        Конструктор склада.

        Параметры:
            name: Наименование склада (до 50 символов)
            address: Адрес расположения склада / помещения
        """
        super().__init__()
        self.name = name
        self.address = address

    @property
    def address(self):
        """
        Возвращает адрес склада.
        """
        return self.__address

    @address.setter
    def address(self, value):
        """
        Задаёт адрес склада.
        """
        if not isinstance(value, str):
            raise argument_exception("address", "Адрес должен быть строкой")

        self.__address = value.strip()

from Src.Core.abstract_model import name_id
from Src.Core.exception import argument_exception, max_length_exception
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model


class nomenclature_model(name_id):
    """
    Модель номенклатуры.
    Позиция учёта с кратким и полным наименованием, группой и единицей измерения.
    """

    # Максимальная длина полного наименования
    __max_full_name_length = 255

    def __init__(self, name="", full_name="", group=None, range=None):
        """
        Конструктор номенклатуры.

        Параметры:
            name: Краткое наименование (до 50 символов)
            full_name: Полное наименование (до 255 символов)
            group: Группа номенклатуры (экземпляр nomenclature_group_model)
            range: Единица измерения (экземпляр range_model)
        """
        super().__init__()
        self.name = name
        self.full_name = full_name
        self.group = group
        self.range = range

    @property
    def full_name(self):
        """
        Возвращает полное наименование номенклатуры.
        """
        return self.__full_name

    @full_name.setter
    def full_name(self, value):
        """
        Задаёт полное наименование номенклатуры. Максимальная длина — 255 символов.
        """
        if value is None or str(value).strip() == "":
            raise argument_exception("full_name", "Полное наименование не должно быть пустым")

        value = str(value).strip()

        if len(value) > self.__max_full_name_length:
            raise max_length_exception("full_name", len(value), self.__max_full_name_length)

        self.__full_name = value

    @property
    def group(self):
        """
        Возвращает группу номенклатуры.
        """
        return self.__group

    @group.setter
    def group(self, value):
        """
        Задаёт группу номенклатуры. Должен быть экземпляром nomenclature_group_model.
        """
        if not isinstance(value, nomenclature_group_model):
            raise argument_exception("group", "Группа должна быть типа nomenclature_group_model")

        self.__group = value

    @property
    def range(self):
        """
        Возвращает единицу измерения номенклатуры.
        """
        return self.__range

    @range.setter
    def range(self, value):
        """
        Задаёт единицу измерения номенклатуры. Должен быть экземпляром range_model.
        """
        if not isinstance(value, range_model):
            raise argument_exception("range", "Единица измерения должна быть типа range_model")

        self.__range = value

    @staticmethod
    def create_flour(group, range_unit):
        """Фабричный метод: Мука пшеничная."""
        return nomenclature_model("Мука пшеничная", "Мука пшеничная высший сорт", group, range_unit)

    @staticmethod
    def create_milk(group, range_unit):
        """Фабричный метод: Молоко 3.2%."""
        return nomenclature_model("Молоко 3.2%", "Молоко коровье пастеризованное 3.2%", group, range_unit)

    @staticmethod
    def create_eggs(group, range_unit):
        """Фабричный метод: Яйца куриные."""
        return nomenclature_model("Яйца куриные", "Яйца куриные столовые С0", group, range_unit)

    @staticmethod
    def create_butter(group, range_unit):
        """Фабричный метод: Масло сливочное."""
        return nomenclature_model("Масло сливочное", "Масло сливочное крестьянское 72.5%", group, range_unit)

    @staticmethod
    def create_sugar(group, range_unit):
        """Фабричный метод: Сахар."""
        return nomenclature_model("Сахар", "Сахар белый кристаллический", group, range_unit)

    @staticmethod
    def create_salt(group, range_unit):
        """Фабричный метод: Соль."""
        return nomenclature_model("Соль", "Соль поваренная пищевая", group, range_unit)

    @staticmethod
    def create_pancake_dough(group, range_unit):
        """Фабричный метод: Полуфабрикат 'Тесто для блинов'."""
        return nomenclature_model("Тесто для блинов", "Тесто блинное жидкое полуфабрикат", group, range_unit)

    @staticmethod
    def create_pancakes(group, range_unit):
        """Фабричный метод: Готовое блюдо 'Блины классические'."""
        return nomenclature_model("Блины классические", "Блины классические тонкие", group, range_unit)

    @staticmethod
    def create_primary_list(groups: dict, ranges: dict) -> list:
        """
        Фабричный метод: создать первичный список номенклатуры под технологическую карту.
        """
        grocery = groups.get("Бакалея")
        dairy = groups.get("Молочные продукты")
        dishes = groups.get("Блюда")

        kg = ranges.get("килограмм")
        liter = ranges.get("литр")
        piece = ranges.get("штука")

        return [
            nomenclature_model.create_flour(grocery, kg),
            nomenclature_model.create_milk(dairy, liter),
            nomenclature_model.create_eggs(dairy, piece),
            nomenclature_model.create_butter(dairy, kg),
            nomenclature_model.create_sugar(grocery, kg),
            nomenclature_model.create_salt(grocery, kg),
            nomenclature_model.create_pancake_dough(dishes, piece),
            nomenclature_model.create_pancakes(dishes, piece),
        ]

from Src.Core.abstract_model import name_id
from Src.Core.exception import argument_exception


class range_model(name_id):
    """
    Модель единицы измерения.
    Содержит базовую единицу измерения и коэффициент пересчёта.
    """

    def __init__(self, name="", conversion_factor=1, base_range=None):
        """
        Конструктор единицы измерения.

        Параметры:
            name: Наименование единицы (например, "грамм", "кг")
            conversion_factor: Коэффициент пересчёта относительно базовой единицы
            base_range: Базовая единица измерения (экземпляр range_model). Для базовой единицы передаётся None
        """
        super().__init__()
        self.__conversion_factor = 1
        self.__base_range = None
        if name and str(name).strip() != "":
            self.name = name
        self.conversion_factor = conversion_factor
        self.base_range = base_range

    @property
    def conversion_factor(self):
        """
        Возвращает коэффициент пересчёта относительно базовой единицы измерения.
        """
        return self.__conversion_factor

    @conversion_factor.setter
    def conversion_factor(self, value):
        """
        Задаёт коэффициент пересчёта. Должен быть положительным числом.
        """
        if not isinstance(value, (int, float)):
            raise argument_exception("conversion_factor", "Коэффициент пересчёта должен быть числом")

        if value <= 0:
            raise argument_exception("conversion_factor", "Коэффициент пересчёта должен быть больше нуля")

        self.__conversion_factor = value

    @property
    def coefficient(self):
        """
        Псевдоним для conversion_factor.
        """
        return self.__conversion_factor

    @property
    def value(self):
        """
        Значение коэффициента пересчёта (псевдоним для conversion_factor).
        """
        return self.__conversion_factor

    @value.setter
    def value(self, val):
        self.conversion_factor = val

    @property
    def base_range(self):
        """
        Возвращает базовую единицу измерения.
        Для базовой единицы возвращает None.
        """
        return self.__base_range

    @base_range.setter
    def base_range(self, value):
        """
        Задаёт базовую единицу измерения. Для базовой единицы устанавливается None.
        """
        if value is not None and not isinstance(value, range_model):
            raise argument_exception("base_range", "Базовая единица измерения должна быть типа range_model")

        self.__base_range = value

    @property
    def base(self):
        """
        Псевдоним для base_range.
        """
        return self.__base_range

    @base.setter
    def base(self, value):
        self.base_range = value

    @staticmethod
    def create_killogramm():
        """
        Фабричный метод - создать килограмм.
        """
        gramm = range_model()
        gramm.name = "Грамм"

        result = range_model()
        result.value = 1000
        result.base = gramm
        result.name = "Килограмм"

        return result
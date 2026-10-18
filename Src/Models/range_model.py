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
        """
        Устанавливает значение коэффициента пересчёта (псевдоним для conversion_factor).
        """
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
        """
        Устанавливает базовую единицу измерения (псевдоним для base_range).
        """
        self.base_range = value

    @staticmethod
    def create_gram(name: str = "грамм"):
        """
        Фабричный метод - создать грамм.
        """
        result = range_model()
        result.name = name
        result.value = 1
        return result

    @staticmethod
    def create_kilogram(name: str = "килограмм", base_name: str = "грамм"):
        """
        Фабричный метод - создать килограмм.
        """
        gram = range_model.create_gram(name=base_name)

        result = range_model()
        result.value = 1000
        result.base = gram
        result.name = name

        return result

    @staticmethod
    def create_milliliter(name: str = "миллилитр"):
        """
        Фабричный метод - создать миллилитр.
        """
        result = range_model()
        result.name = name
        result.value = 1
        return result

    @staticmethod
    def create_liter(name: str = "литр", base_name: str = "миллилитр"):
        """
        Фабричный метод - создать литр с базовой единицей миллилитр.
        """
        ml = range_model.create_milliliter(name=base_name)
        result = range_model()
        result.value = 1000
        result.base = ml
        result.name = name
        return result

    @staticmethod
    def create_piece(name: str = "штука"):
        """
        Фабричный метод - создать штуку.
        """
        result = range_model()
        result.name = name
        result.value = 1
        return result

    def get_report_title(self) -> str:
        """Человекочитаемое наименование типа сущности."""
        return "Единица измерения"

    def get_report_tag(self) -> str:
        """XML/HTML тег типа сущности."""
        return "range"

    def get_report_headers(self) -> list:
        """Заголовки таблицы отчета для единицы измерения."""
        return ["Код", "Наименование", "Коэффициент", "Базовая единица"]

    def get_report_rows(self) -> list:
        """Строки таблицы отчета для единицы измерения."""
        code = str(getattr(self, "unique_code", getattr(self, "id", "")))
        name = str(getattr(self, "name", ""))
        factor = str(getattr(self, "conversion_factor", 1))
        base_name = str(self.base_range.name) if getattr(self, "base_range", None) else "базовая"
        return [[code, name, factor, base_name]]

    def get_report_fields(self) -> dict:
        """Словарь полей для XML/структурированных представлений."""
        factor = str(getattr(self, "conversion_factor", 1))
        base_name = self.base_range.name if getattr(self, "base_range", None) else ""
        return {
            "conversion_factor": str(factor),
            "base_range": str(base_name),
        }
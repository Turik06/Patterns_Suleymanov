from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator
from Src.Logics.settings_manager import settings_manager
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model


class storage_manager(abstract_manager):
    """
    Менеджер хранения доменных моделей.
    При первом старте (is_first_start == True) формирует первичные справочники.
    """

    _storages: dict = None
    _ranges: dict = None
    _nomenclatures: dict = None
    _groups: dict = None
    __is_initialized: bool = False

    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
            cls.instance._storages = {}
            cls.instance._ranges = {}
            cls.instance._nomenclatures = {}
            cls.instance._groups = {}
            cls.instance.__is_initialized = False
        return cls.instance

    def convert(self) -> bool:
        """
        Переопределенный метод abstract_manager.
        Если запуск первый (is_first_start == True) — генерирует первичные данные.
        """
        if self.__is_initialized:
            return True

        try:
            s_manager = settings_manager()
            if not s_manager.is_loaded:
                s_manager.load()

            settings = s_manager.settings
            if settings and settings.is_first_start:
                self._initialize_primary_data()

            self.__is_initialized = True
            return True
        except Exception:
            return False

    def _initialize_primary_data(self) -> None:
        """
        Инициализация первичных данных.
        Порядок важен: номенклатура зависит от единиц измерения и групп.
        """
        self.__create_ranges()
        self.__create_groups()
        self.__create_nomenclatures()
        self.__create_storages()

    def __create_ranges(self) -> None:
        """Генерация базовых и производных единиц измерения."""
        gram = range_model(name="грамм", conversion_factor=1, base_range=None)
        kilogram = range_model(name="килограмм", conversion_factor=1000, base_range=gram)
        piece = range_model(name="штука", conversion_factor=1, base_range=None)
        liter = range_model(name="литр", conversion_factor=1, base_range=None)
        milliliter = range_model(name="миллилитр", conversion_factor=0.001, base_range=liter)

        for r in (gram, kilogram, piece, liter, milliliter):
            self.add_range(r)

    def __create_groups(self) -> None:
        """Генерация групп номенклатуры под технологическую карту."""
        grocery = nomenclature_group_model(name="Бакалея")
        dairy = nomenclature_group_model(name="Молочные продукты")

        self.add_group(grocery)
        self.add_group(dairy)

    def __create_nomenclatures(self) -> None:
        """Генерация номенклатуры (ингредиенты для рецепта)."""
        groups_by_name = {g.name: g for g in self._groups.values()}
        ranges_by_name = {r.name: r for r in self._ranges.values()}

        grocery = groups_by_name.get("Бакалея")
        dairy = groups_by_name.get("Молочные продукты")

        kg = ranges_by_name.get("килограмм")
        liter = ranges_by_name.get("литр")
        piece = ranges_by_name.get("штука")

        items = [
            nomenclature_model("Мука пшеничная", "Мука пшеничная высший сорт", grocery, kg),
            nomenclature_model("Молоко 3.2%", "Молоко коровье пастеризованное 3.2%", dairy, liter),
            nomenclature_model("Яйца куриные", "Яйца куриные столовые С0", dairy, piece),
            nomenclature_model("Масло сливочное", "Масло сливочное крестьянское 72.5%", dairy, kg),
            nomenclature_model("Сахар", "Сахар белый кристаллический", grocery, kg),
            nomenclature_model("Соль", "Соль поваренная пищевая", grocery, kg),
        ]

        for item in items:
            self.add_nomenclature(item)

    def __create_storages(self) -> None:
        """Генерация складов."""
        main_storage = storage_model(name="Основной склад", address="ул. Промышленная, 5, пом. 101")
        fridge = storage_model(name="Холодильник цеха", address="ул. Промышленная, 5, пом. 102")

        self.add_storage(main_storage)
        self.add_storage(fridge)


    def add_storage(self, item: storage_model) -> bool:
        """Добавить склад. Возвращает True, если добавлен; False, если дубликат или неверный тип."""
        if not isinstance(item, storage_model) or item.id in self._storages:
            return False
        self._storages[item.id] = item
        return True

    def add_range(self, item: range_model) -> bool:
        """Добавить единицу измерения."""
        if not isinstance(item, range_model) or item.id in self._ranges:
            return False
        self._ranges[item.id] = item
        return True

    def add_nomenclature(self, item: nomenclature_model) -> bool:
        """Добавить позицию номенклатуры."""
        if not isinstance(item, nomenclature_model) or item.id in self._nomenclatures:
            return False
        self._nomenclatures[item.id] = item
        return True

    def add_group(self, item: nomenclature_group_model) -> bool:
        """Добавить группу номенклатуры."""
        if not isinstance(item, nomenclature_group_model) or item.id in self._groups:
            return False
        self._groups[item.id] = item
        return True



    @property
    def storages(self) -> dict:
        """Словарь складов {id: storage_model}."""
        return self._storages

    @property
    def ranges(self) -> dict:
        """Словарь единиц измерения {id: range_model}."""
        return self._ranges

    @property
    def nomenclatures(self) -> dict:
        """Словарь номенклатуры {id: nomenclature_model}."""
        return self._nomenclatures

    @property
    def groups(self) -> dict:
        """Словарь групп номенклатуры {id: nomenclature_group_model}."""
        return self._groups

    @property
    def data(self) -> dict:
        """Все данные хранилища по категориям."""
        return {
            "storages": self._storages,
            "ranges": self._ranges,
            "nomenclatures": self._nomenclatures,
            "groups": self._groups
        }

    @property
    def is_initialized(self) -> bool:
        """Флаг завершения инициализации."""
        return self.__is_initialized

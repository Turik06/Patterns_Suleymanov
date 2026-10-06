from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator
from Src.Logics.settings_manager import settings_manager
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.recipe_model import recipe_model


class storage_manager(abstract_manager):
    """
    Менеджер хранения доменных моделей.
    При первом старте (is_first_start == True) формирует первичные справочники.
    """

    _storages: dict = None
    _ranges: dict = None
    _nomenclatures: dict = None
    _groups: dict = None
    _recipes: dict = None
    __is_initialized: bool = False

    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
            cls.instance._storages = {}
            cls.instance._ranges = {}
            cls.instance._nomenclatures = {}
            cls.instance._groups = {}
            cls.instance._recipes = {}
            cls.instance.__is_initialized = False
        return cls.instance

    def convert(self, settings=None) -> bool:
        """
        Переопределенный метод abstract_manager.
        Если запуск первый (is_first_start == True) — генерирует первичные данные.
        При передаче settings извне — использует переданный объект (для тестов).
        """
        if self.__is_initialized:
            return True

        try:
            if settings is None:
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
        Инициализация первичных данных с использованием фабричных методов доменных моделей.
        Порядок важен: номенклатура зависит от единиц измерения и групп, а рецепты — от номенклатуры.
        """
        self.__create_ranges()

        # Группы номенклатуры
        for group in nomenclature_group_model.create_primary_list():
            self.add_group(group)

        # Склады
        for storage in storage_model.create_primary_list():
            self.add_storage(storage)

        # Номенклатура
        groups = {g.name: g for g in self._groups.values()}
        ranges = {r.name: r for r in self._ranges.values()}
        for item in nomenclature_model.create_primary_list(groups, ranges):
            self.add_nomenclature(item)

        # Технологические карты (рецепты)
        nomenclatures = {n.name: n for n in self._nomenclatures.values()}
        for recipe in recipe_model.create_primary_list(nomenclatures):
            self.add_recipe(recipe)

    def __create_ranges(self) -> None:
        """Генерация базовых и производных единиц измерения с использованием фабричных методов."""
        kilogram = range_model.create_kilogram()
        gram = kilogram.base
        liter = range_model.create_liter()
        milliliter = liter.base
        piece = range_model.create_piece()

        for r in (gram, kilogram, milliliter, liter, piece):
            self.add_range(r)

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

    def add_recipe(self, item: recipe_model) -> bool:
        """Добавить технологическую карту (рецепт)."""
        if not isinstance(item, recipe_model) or item.id in self._recipes:
            return False
        self._recipes[item.id] = item
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
    def recipes(self) -> dict:
        """Словарь технологических карт {id: recipe_model}."""
        return self._recipes

    @property
    def data(self) -> dict:
        """Все данные хранилища по категориям."""
        return {
            "storages": self._storages,
            "ranges": self._ranges,
            "nomenclatures": self._nomenclatures,
            "groups": self._groups,
            "recipes": self._recipes,
        }

    @property
    def is_initialized(self) -> bool:
        """Флаг завершения инициализации."""
        return self.__is_initialized

    @property
    def is_loaded(self) -> bool:
        """Флаг готовности данных (переопределение abstract_manager)."""
        return self.__is_initialized

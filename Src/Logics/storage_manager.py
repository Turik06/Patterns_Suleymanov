from Src.Core.abstract_manager import abstract_manager
from Src.Core.common import common
from Src.Core.validator import validator
from Src.Logics.settings_manager import settings_manager
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.recipe_model import recipe_model
from Src.Models.transaction_model import transaction_model
from Src.Logics.storage_reposity import storage_repository
from Src.Core.event_type import event_type
from Src.Logics.observer import observer


class storage_dict(dict):
    """
    Словарь сущностей с поддержкой индексации по номеру
    """
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


recipe_dict = storage_dict


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
    _transactions: dict = None
    __repository: storage_repository = None
    __is_initialized: bool = False

    # Singleton
    def __new__(cls, *args, **kwargs):
        """
        Реализация шаблона Singleton. Возвращает единственный экземпляр класса.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self, settings=None):
        """
        Инициализация хранилища
        """
        if settings is not None:
            self._settings = settings

        if not hasattr(self, "_storages") or self._storages is None:
            self._storages = storage_dict()
            self._ranges = storage_dict()
            self._nomenclatures = storage_dict()
            self._groups = storage_dict()
            self._recipes = storage_dict()
            self._transactions = storage_dict()
            self.__repository = storage_repository()
            self.__is_initialized = False

    def build(self, settings=None) -> bool:
        """
        Генерация первичных данных
        """
        if settings is not None:
            self._settings = settings
        self.convert(getattr(self, "_settings", None))
        if len(self._ranges) == 0:
            self._initialize_primary_data()
        return True

    def load(self, settings=None) -> bool:
        """
        Загрузка данных в хранилище (алиас для convert).
        """
        return self.convert(settings)

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
        """Добавить склад"""
        if not isinstance(item, storage_model) or item.id in self._storages:
            return False
        self._storages[item.id] = item
        if self.__repository is not None:
            self.__repository.registry(item)
        observer.create(event_type.storage_operation(), {"operation": "add_storage", "id": item.id, "name": getattr(item, "name", "")})
        return True

    def add_range(self, item: range_model) -> bool:
        """Добавить единицу измерения"""
        if not isinstance(item, range_model) or item.id in self._ranges:
            return False
        self._ranges[item.id] = item
        if self.__repository is not None:
            self.__repository.registry(item)
        return True

    def add_nomenclature(self, item: nomenclature_model) -> bool:
        """Добавить номенклатуру"""
        if not isinstance(item, nomenclature_model) or item.id in self._nomenclatures:
            return False
        self._nomenclatures[item.id] = item
        if self.__repository is not None:
            self.__repository.registry(item)
        return True

    def add_group(self, item: nomenclature_group_model) -> bool:
        """Добавить группу номенклатуры"""
        if not isinstance(item, nomenclature_group_model) or item.id in self._groups:
            return False
        self._groups[item.id] = item
        if self.__repository is not None:
            self.__repository.registry(item)
        return True

    def add_recipe(self, item: recipe_model) -> bool:
        """Добавить рецепт"""
        if not isinstance(item, recipe_model) or item.id in self._recipes:
            return False
        self._recipes[item.id] = item
        if self.__repository is not None:
            if hasattr(item, "rows") and item.rows:
                self.__repository.registry_range(item.rows)
            self.__repository.registry(item)
        return True

    def add_transaction(self, item: transaction_model) -> bool:
        """Добавить складскую транзакцию"""
        if not isinstance(item, transaction_model) or item.id in self._transactions:
            return False
        self._transactions[item.id] = item
        if self.__repository is not None:
            self.__repository.registry(item)
        observer.create(event_type.storage_operation(), {"operation": "add_transaction", "id": item.id, "value": item.value})
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
    def transactions(self) -> dict:
        """Складские транзакции."""
        return self._transactions

    @staticmethod
    def storage_key() -> str:
        """Ключ категории складов"""
        return "storage_model"

    @staticmethod
    def transaction_key() -> str:
        """Ключ категории складских транзакций"""
        return "transaction_model"

    @staticmethod
    def range_key() -> str:
        """Ключ категории единиц измерения"""
        return "range_model"

    @staticmethod
    def group_key() -> str:
        """Ключ категории групп номенклатуры"""
        return "group_model"

    @staticmethod
    def nomenclature_key() -> str:
        """Ключ категории номенклатуры"""
        return "nomenclature_model"

    @staticmethod
    def receipt_key() -> str:
        """Ключ категории технологических карт"""
        return "receipt_model"

    @staticmethod
    def recipe_key() -> str:
        """Ключ категории рецептов (синоним receipt_model)"""
        return "receipt_model"

    @staticmethod
    def recipe_row_key() -> str:
        """Ключ для строк рецептов"""
        return "recipe_row_model"

    @classmethod
    def keys(cls) -> list:
        """
        Получить список всех зарегистрированных ключей категорий хранилища через рефлексию.
        """
        methods = [
            method for method in dir(cls)
            if callable(getattr(cls, method, None)) and method.endswith('_key')
        ]
        return [getattr(cls, method)() for method in methods]

    """
    Получить список всех ключей и описания к ним
    """
    @staticmethod
    def domains() -> dict:
        return common.domains(storage_manager)

    @property
    def data(self) -> dict:
        """Все данные хранилища в виде списков"""
        rows = []
        for recipe in self._recipes.values():
            rows.extend(recipe.items)

        return {
            self.group_key(): list(self._groups.values()),
            self.recipe_row_key(): rows,
            self.nomenclature_key(): list(self._nomenclatures.values()),
            self.range_key(): list(self._ranges.values()),
            self.receipt_key(): list(self._recipes.values()),
            self.storage_key(): list(self._storages.values()),
            self.transaction_key(): list(self._transactions.values()),
        }

    @property
    def is_initialized(self) -> bool:
        """Флаг завершения инициализации."""
        return self.__is_initialized

    @property
    def is_loaded(self) -> bool:
        """Флаг готовности данных (переопределение abstract_manager)."""
        return self.__is_initialized

    def clear(self) -> None:
        """
        Очистить все словари хранилища и сбросить флаг инициализации.
        """
        self._storages = storage_dict()
        self._ranges = storage_dict()
        self._nomenclatures = storage_dict()
        self._groups = storage_dict()
        self._recipes = storage_dict()
        self._transactions = storage_dict()
        self.__repository = storage_repository()
        self.__is_initialized = False

    def first_start(self) -> None:
        """
        Первоначальное наполнение хранилища первичными данными.
        """
        self.clear()
        self._initialize_primary_data()
        self.__is_initialized = True

    def resolve_category(self, entity_type: str):
        """
        Разрешение наименования типа сущности в ключ категории хранилища через рефлексию.
        """
        if not isinstance(entity_type, str):
            return None
        normalized = entity_type.strip().lower()

        # Поиск по методам *_key через рефлексию
        for method_name in dir(self.__class__):
            if method_name.endswith("_key"):
                method = getattr(self.__class__, method_name, None)
                if callable(method):
                    key_val = method()
                    clean_method = method_name[:-4].lower()
                    clean_key = key_val.lower().replace("_model", "").replace("_key", "")
                    if normalized in (clean_method, clean_key, key_val.lower()):
                        return key_val
                    if normalized in (f"{clean_method}s", f"{clean_key}s"):
                        return key_val

        # Поиск по публичным свойствам-словарям хранилища
        for prop_name in dir(self):
            if prop_name.startswith("_"):
                continue
            prop_val = getattr(self, prop_name, None)
            if isinstance(prop_val, dict):
                prop_clean = prop_name.rstrip("s").lower()
                if normalized in (prop_name.lower(), prop_clean):
                    return prop_name

        return None

    def get_by_type_and_id(self, entity_type: str, identifier: str = ""):
        """
        Полиморфный поиск сущности в хранилище по ее типу и идентификатору или наименованию.
        """
        cat_key = self.resolve_category(entity_type)
        if not cat_key:
            return None
        catalog = self.data.get(cat_key)
        if not catalog:
            return None

        items = list(catalog.values()) if isinstance(catalog, dict) else list(catalog)
        if not items:
            return None

        clean_id = (identifier or "").strip()
        if not clean_id:
            return items[0]

        clean_id_lower = clean_id.lower()
        for item in items:
            if (
                getattr(item, "unique_code", None) == clean_id
                or getattr(item, "id", None) == clean_id
                or getattr(item, "name", "").lower() == clean_id_lower
            ):
                return item

        if clean_id.isdigit():
            idx = int(clean_id)
            if 0 <= idx < len(items):
                return items[idx]

        return None

    def get_recipe(self, identifier: str = ""):
        """Поиск технологической карты по коду или имени."""
        return self.get_by_type_and_id("recipe", identifier)

    def get_nomenclature(self, identifier: str = ""):
        """Поиск номенклатуры по коду или имени."""
        return self.get_by_type_and_id("nomenclature", identifier)

    def get_range(self, identifier: str = ""):
        """Поиск единицы измерения по коду или имени."""
        return self.get_by_type_and_id("range", identifier)

    def get_catalog(self, entity_type: str) -> dict:
        """Получить словарь сущностей по типу"""
        category = self.resolve_category(entity_type)
        if category == self.range_key():
            return self._ranges
        elif category == self.group_key():
            return self._groups
        elif category == self.nomenclature_key():
            return self._nomenclatures
        elif category == self.receipt_key() or category == self.recipe_key():
            return self._recipes
        elif category == self.storage_key():
            return self._storages
        elif category == self.transaction_key():
            return self._transactions
        return None

    def save_entity(self, entity) -> bool:
        """Сохранить сущность в хранилище"""
        if isinstance(entity, range_model):
            return self.add_range(entity)
        elif isinstance(entity, nomenclature_group_model):
            return self.add_group(entity)
        elif isinstance(entity, nomenclature_model):
            return self.add_nomenclature(entity)
        elif isinstance(entity, recipe_model):
            return self.add_recipe(entity)
        elif isinstance(entity, storage_model):
            return self.add_storage(entity)
        elif isinstance(entity, transaction_model):
            return self.add_transaction(entity)
        return False

    def delete_entity(self, entity_type: str, unique_code: str) -> bool:
        """Удалить сущность"""
        catalog = self.get_catalog(entity_type)
        if catalog is not None and unique_code in catalog:
            item = catalog[unique_code]
            if self.__repository is not None and unique_code in self.__repository.data:
                try:
                    self.__repository.delete(item)
                except Exception:
                    self.__repository.data.pop(unique_code, None)
                    self.__repository.counts.pop(unique_code, None)
            del catalog[unique_code]
            return True
        return False

    @property
    def repository(self) -> storage_repository:
        """Репозиторий данных"""
        return self.__repository

    def find_referrers(self, unique_code: str) -> list:
        """Поиск ссылающихся объектов"""
        from Src.Logics.entity_service import entity_service
        return entity_service(self).find_referrers(unique_code)

    def is_linked(self, entity_type: str, unique_code: str) -> bool:
        """Проверка связей"""
        from Src.Logics.entity_service import entity_service
        return entity_service(self).is_linked(unique_code)

from Src.Core.abstract_manager import abstract_manager
from Src.Core.common import common
from Src.Core.validator import validator
from Src.Logics.settings_manager import settings_manager
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.recipe_model import recipe_model


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

    @staticmethod
    def storage_key() -> str:
        """Ключ категории складов"""
        return "storage_model"

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
        return False

    def delete_entity(self, entity_type: str, unique_code: str) -> bool:
        """Удалить сущность из хранилища"""
        catalog = self.get_catalog(entity_type)
        if catalog is not None and unique_code in catalog:
            del catalog[unique_code]
            return True
        return False

    def find_referrers(self, unique_code: str) -> list:
        """Ищет объекты, которые ссылаются на этот код."""
        if not unique_code:
            return []

        referrers = []
        all_items = []
        for catalog in (self._ranges, self._groups, self._nomenclatures, self._recipes, self._storages):
            all_items.extend(catalog.values())

        for item in all_items:
            if getattr(item, "unique_code", None) == unique_code:
                continue

            for ref in item.references():
                if getattr(ref, "unique_code", None) == unique_code:
                    referrers.append(item)
                    break

        return referrers

    def is_linked(self, entity_type: str, unique_code: str) -> bool:
        """Есть ли ссылки на эту сущность."""
        return len(self.find_referrers(unique_code)) > 0

    def validate_dependencies_exist(self, entity) -> tuple[bool, str]:
        """Проверка существования зависимостей."""
        if isinstance(entity, range_model) and entity.base:
            base_code = entity.base.unique_code
            if base_code not in self._ranges:
                return False, f"Базовая единица измерения '{base_code}' не найдена"

        if isinstance(entity, nomenclature_model):
            if entity.group and entity.group.unique_code not in self._groups:
                return False, f"Группа '{entity.group.unique_code}' не найдена"
            if entity.range and entity.range.unique_code not in self._ranges:
                return False, f"Единица измерения '{entity.range.unique_code}' не найдена"

        if isinstance(entity, recipe_model):
            for row in getattr(entity, "rows", []):
                if row.nomenclature and row.nomenclature.unique_code not in self._nomenclatures:
                    return False, f"Номенклатура '{row.nomenclature.name}' не найдена"
                if row.range and row.range.unique_code not in self._ranges:
                    return False, f"Единица измерения '{row.range.name}' не найдена"

        return True, ""

    def create_entity_from_dict(self, entity_type: str, payload: dict, worker=None):
        """Создает и сохраняет сущность из словаря."""
        category = self.resolve_category(entity_type)
        if not category or category not in self.data:
            raise ValueError(f"Неизвестный тип сущности '{entity_type}'")

        if worker is None:
            from Src.Logics.convertor import convertor
            worker = convertor()

        dto = worker.resolve_dto(payload, type_hint=entity_type) or worker.resolve_dto(payload, type_hint=category)
        if not dto:
            raise ValueError("Не удалось создать объект из данных")

        base_code = getattr(dto, "base_code", "") or payload.get("base_code")
        if base_code and base_code not in self.ranges:
            raise ValueError(f"Базовая единица измерения '{base_code}' не найдена")

        group_code = getattr(dto, "group_code", "") or payload.get("group_code")
        if group_code and group_code not in self.groups:
            raise ValueError(f"Группа номенклатуры '{group_code}' не найдена")

        range_code = getattr(dto, "range_code", "") or payload.get("range_code")
        if range_code and range_code not in self.ranges:
            raise ValueError(f"Единица измерения '{range_code}' не найдена")

        from Src.Logics.mapping_factory import mapping_factory
        resolver = {}
        for cat in (self.ranges, self.groups, self.nomenclatures, self.recipes, self.storages):
            resolver.update(cat)

        model = mapping_factory().to_model(dto, resolver)
        if not model:
            raise ValueError("Не удалось создать объект из данных")

        is_valid, msg = self.validate_dependencies_exist(model)
        if not is_valid:
            raise ValueError(msg)

        catalog = self.get_catalog(entity_type)
        if catalog is not None and model.unique_code in catalog:
            raise ValueError(f"Сущность '{model.unique_code}' уже существует")

        self.save_entity(model)
        return model

    def update_entity_from_dict(self, entity_type: str, unique_code: str, payload: dict):
        """Обновляет поля сущности из словаря."""
        category = self.resolve_category(entity_type)
        if not category or category not in self.data:
            raise ValueError(f"Неизвестный тип сущности '{entity_type}'")

        catalog = self.get_catalog(entity_type)
        entity = catalog.get(unique_code) if catalog is not None else None
        if not entity:
            raise LookupError(f"Сущность '{unique_code}' не найдена")

        new_code = payload.get("unique_code") or payload.get("id")
        changing_code = bool(new_code and new_code != unique_code)

        if changing_code:
            if self.is_linked(category, unique_code):
                raise PermissionError(f"Нельзя менять код связанной сущности '{unique_code}'")
            if new_code in catalog:
                raise ValueError(f"Сущность с кодом '{new_code}' уже существует")

        fields_to_update = {}
        for key, val in payload.items():
            if key in ("unique_code", "id", "type"):
                continue
            if hasattr(entity, key) and val is not None:
                fields_to_update[key] = val

        old_values = {key: getattr(entity, key) for key in fields_to_update}

        try:
            for key, val in fields_to_update.items():
                setattr(entity, key, val)
        except Exception as ex:
            for key, old_val in old_values.items():
                setattr(entity, key, old_val)
            raise ValueError(f"Ошибка валидации поля: {ex}") from ex

        if changing_code:
            del catalog[unique_code]
            entity.unique_code = new_code
            catalog[new_code] = entity

        return entity

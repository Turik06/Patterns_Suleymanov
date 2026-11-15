# Хранилище данных и сервис сущностей (storage_manager & entity_service)

## 1. UML-диаграмма классов

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        +load(file_name: str) None
        +convert() bool
        +is_loaded: bool
    }

    class storage_manager {
        <<Singleton>>
        -_storages: dict
        -_ranges: dict
        -_nomenclatures: dict
        -_groups: dict
        -_recipes: dict
        -__is_initialized: bool
        +__new__(cls) storage_manager
        +first_start() void
        +clear() void
        +convert(settings: settings_model = None) bool
        +resolve_category(entity_type: str) str
        +get_catalog(entity_type: str) dict
        +get_by_type_and_id(entity_type: str, identifier: str) object
        +save_entity(entity) bool
        +delete_entity(entity_type: str, unique_code: str) bool
        +add_storage(item) bool
        +add_range(item) bool
        +add_nomenclature(item) bool
        +add_group(item) bool
        +add_recipe(item) bool
        +storages: dict
        +ranges: dict
        +nomenclatures: dict
        +groups: dict
        +recipes: dict
        +data: dict
        +is_initialized: bool
        +is_loaded: bool
    }

    class entity_service {
        -storage_manager __storage
        +storage: storage_manager
        +get_catalog(entity_type: str) dict
        +find_referrers(unique_code: str) list
        +is_linked(unique_code: str) bool
        +validate_dependencies_exist(dto, entity) tuple
        +get_entity(entity_type: str, unique_code: str) object
        +create_entity(entity_type: str, payload: dict, worker) object
        +update_entity(entity_type: str, unique_code: str, payload: dict) object
        +delete_entity(entity_type: str, unique_code: str) bool
    }

    class settings_manager {
        <<Singleton>>
        +settings: settings_model
    }

    class storage_model {
        -__address: str
        +address: str
    }

    class range_model {
        -__conversion_factor: float
        -__base_range: range_model
        +conversion_factor: float
        +base_range: range_model
    }

    class nomenclature_group_model {
    }

    class nomenclature_model {
        -__full_name: str
        -__group: nomenclature_group_model
        -__range: range_model
        +full_name: str
        +group: nomenclature_group_model
        +range: range_model
    }

    class recipe_model {
        -__dish: nomenclature_model
        -__rows: list
        +dish: nomenclature_model
        +rows: list
        +portions: int
        +brutto: float
        +netto: float
    }

    class name_id {
        <<abstract>>
        -__name: str
        -__id: str
        +name: str
        +id: str
    }

    name_id <|-- storage_model
    name_id <|-- range_model
    name_id <|-- nomenclature_group_model
    name_id <|-- nomenclature_model
    name_id <|-- recipe_model

    abstract_manager <|-- storage_manager

    entity_service o-- storage_manager : __storage

    storage_manager o-- storage_model : _storages
    storage_manager o-- range_model : _ranges
    storage_manager o-- nomenclature_group_model : _groups
    storage_manager o-- nomenclature_model : _nomenclatures
    storage_manager o-- recipe_model : _recipes

    storage_manager ..> settings_manager : uses

    nomenclature_model o-- nomenclature_group_model : group
    nomenclature_model o-- range_model : range
    range_model o-- range_model : base_range
```

---

## 2. Разделение ответственности

* **`storage_manager`** — низкоуровневое хранилище данных (паттерн *Singleton*):
  * Хранение коллекций доменных объектов в оперативной памяти (`_storages`, `_ranges`, `_nomenclatures`, `_groups`, `_recipes`).
  * Индексация и разрешение категорий сущностей по строковым ключам (`resolve_category`, `get_catalog`).
  * Первичная инициализация справочников (`first_start()`, `_initialize_primary_data()`).
  * Базовые операции добавления (`add_*`, `save_entity`) и удаления по ключу (`delete_entity`).

* **`entity_service`** — сервисный слой для бизнес-логики работы с сущностями:
  * Полный цикл CRUD-операций (`get_entity`, `create_entity`, `update_entity`, `delete_entity`).
  * Проверка уникальности кодов сущностей перед сохранением.
  * Валидация наличия зависимых объектов (`validate_dependencies_exist`) при трансформации DTO в модель.
  * Контроль ссылочной целостности (`find_referrers`, `is_linked`): запрет удаления или модификации уникального кода сущностей, на которые ссылаются другие объекты (`PermissionError`).

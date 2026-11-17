# Менеджер настроек (settings_manager)

## 1. UML-диаграмма классов

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        -__file_name: str
        -__is_loaded: bool
        -__data: list
        +load(file_name: str) None
        +convert() bool
        +is_loaded: bool
    }

    class settings_manager {
        <<Singleton>>
        -__default_file_name: str
        -_settings: settings_model
        -__is_loaded: bool
        -__data: dict
        +__new__(cls) settings_manager
        +load(file_name: str) None
        +build() bool
        +convert() bool
        +convert_report_type(value) report_type_enum
        +is_loaded: bool
        +settings: settings_model
    }

    class settings_model {
        -__organization: organization_model
        -__boss_name: str
        -__account_name: str
        -__is_first_start: bool
        -__response_format: report_type_enum
        +organization: organization_model
        +company: organization_model
        +boss_name: str
        +account_name: str
        +is_first_start: bool
        +response_format: report_type_enum
        +from_dto(dto, resolver) settings_model$
    }

    class abstract_dto {
        <<abstract>>
        +load_dict(data: dict) abstract_dto
    }

    class settings_dto {
        -str __boss_name
        -str __account_name
        -bool __is_first_start
        -str __response_format
        -company_dto __organization
        +boss_name: str
        +account_name: str
        +is_first_start: bool
        +response_format: str
        +organization: company_dto
        +company_name: str
        +load_dict(data: dict) settings_dto
        +from_domain_model(source: settings_model) settings_dto
    }

    class company_dto {
        +name: str
        +inn: str
        +bik: str
        +account: str
        +ownership_form: str
        +from_domain_model(source: organization_model) company_dto
    }

    class report_type_enum {
        <<enumeration>>
        +TXT : 1
        +CSV : 2
        +MARKDOWN : 3
        +XML : 4
        +HTML : 5
        +RTF : 6
    }

    class organization_model {
        -__inn: str
        -__bik: str
        -__account: str
        -__ownership_form: str
        +inn: str
        +bik: str
        +account: str
        +ownership_form: str
    }

    class name_id {
        <<abstract>>
        -__name: str
        -__id: str
        +name: str
        +id: str
        +__eq__(other) bool
    }

    name_id <|-- settings_model
    name_id <|-- organization_model
    abstract_manager <|-- settings_manager

    abstract_dto <|-- settings_dto
    abstract_dto <|-- company_dto

    settings_manager o-- settings_model : _settings
    settings_model o-- organization_model : __organization
    settings_model o-- report_type_enum : __response_format

    settings_dto o-- company_dto : __organization
    settings_manager ..> settings_dto : uses for deserialization
    settings_model ..> settings_dto : from_dto()
```

---

## 2. Механизм десериализации настроек

Загрузка файла `settings.json` выполняется через универсальный конвейер DTO и конвертера:

1. **Чтение JSON:** `settings_manager.load()` считывает файл конфигурации в словарь `__data`.
2. **Преобразование в DTO:** `convertor().deserialize(data)` идентифицирует поля настроек и заполняет `settings_dto` (а также вложенный `company_dto` для карточки организации).
3. **Отображение в модель:** `mapping_factory` вызывает фабричный метод `settings_model.from_dto(dto)`, создавая валидированный экземпляр доменной модели `settings_model`.
4. Поддерживается как структурированный формат (с объектом `organization`), так и плоский формат (с полем `company_name`).

# Прототип и ОСВ

## 1. Диаграмма классов

```mermaid
classDiagram
    direction TB

    class abstract_prototype {
        <<abstract>>
        +clone(filter) abstract_prototype*
    }

    class prototype {
        -list _data
        +data: list
        +filterable_fields: list
        +clone(filter_model: filter_dto) prototype
        +create_osv(start_date=None, end_date=None) prototype
        +_resolve_nested_path(source, parts: list)$ list
        +_extract_values(obj, field_name: str, visited: set)$ list
        +get_filterable_fields(source, max_depth=2)$ list
    }

    class filter_type_enum {
        <<enumeration>>
        +EQUALS: str
        +LIKE: str
        +from_string(val)$ filter_type_enum
    }

    class filter_item_dto {
        -str _field_name
        -filter_type_enum _filter_type
        -Any _value
        +field_name: str
        +filter_type: filter_type_enum
        +value: Any
        +is_match(val) bool
        +to_dict() dict
        +from_dict(data: dict)$ filter_item_dto
    }

    class filter_dto {
        -str _name
        -str _unique_code
        -filter_type_enum _filter_type
        -list _filters
        -datetime _start_date
        -datetime _end_date
        +name: str
        +unique_code: str
        +filter_type: filter_type_enum
        +filters: list
        +start_date: datetime
        +end_date: datetime
        +all_filters: list
        +add(item: filter_item_dto) void
        +to_dict() dict
        +from_dict(data: dict)$ filter_dto
        +from_domain_model(model)$ filter_dto
    }

    class name_id {
        <<abstract>>
        -str __id
        -str __name
        +id: str
        +unique_code: str
        +name: str
        +references() list
    }

    class storage_model {
        -str __address
        +address: str
    }

    class range_model {
        -float __conversion_factor
        -range_model __base_range
        +conversion_factor: float
        +base_range: range_model
        +references() list
    }

    class nomenclature_group_model {
        -nomenclature_group_model __parent
        +parent: nomenclature_group_model
        +references() list
    }

    class nomenclature_model {
        -str __full_name
        -nomenclature_group_model __group
        -range_model __range
        +full_name: str
        +group: nomenclature_group_model
        +range: range_model
        +references() list
    }

    class transaction_model {
        -storage_model __storage
        -nomenclature_model __nomenclature
        -range_model __range
        -float __value
        -datetime __period
        +storage: storage_model
        +nomenclature: nomenclature_model
        +range: range_model
        +value: float
        +period: datetime
        +references() list
    }

    class osv_row_model {
        +storage: storage_model
        +nomenclature: nomenclature_model
        +range: range_model
        +start_balance: float
        +incoming: float
        +outgoing: float
        +final_balance: float
        +references() list
        +to_dict() dict
    }

    abstract_prototype <|-- prototype
    name_id <|-- storage_model
    name_id <|-- range_model
    name_id <|-- nomenclature_group_model
    name_id <|-- nomenclature_model
    name_id <|-- transaction_model
    name_id <|-- osv_row_model

    prototype ..> filter_dto : clone
    prototype ..> osv_row_model : create_osv
    filter_dto *-- filter_item_dto : filters
    filter_dto o-- filter_type_enum : filter_type
    filter_item_dto o-- filter_type_enum : filter_type

    nomenclature_model o-- nomenclature_group_model : group
    nomenclature_model o-- range_model : range
    nomenclature_group_model o-- nomenclature_group_model : parent
    range_model o-- range_model : base_range

    transaction_model o-- storage_model : storage
    transaction_model o-- nomenclature_model : nomenclature
    transaction_model o-- range_model : range

    osv_row_model o-- storage_model : storage
    osv_row_model o-- nomenclature_model : nomenclature
    osv_row_model o-- range_model : range
```

---

## 2. Связи сущностей

```mermaid
flowchart TD
    subgraph Учет
        Tx["Транзакция"]
        OSV["Строка ОСВ"]
    end

    subgraph Справочники
        Wh["Склад"]
        Nom["Номенклатура"]
        Rng["Единица измерения"]
        BaseRng["Базовая единица"]
        Grp["Группа"]
        ParentGrp["Родительская группа"]
    end

    Tx -->|storage| Wh
    Tx -->|nomenclature| Nom
    Tx -->|range| Rng

    OSV -->|storage| Wh
    OSV -->|nomenclature| Nom
    OSV -->|range| Rng

    Nom -->|group| Grp
    Nom -->|range| Rng
    Grp -->|parent| ParentGrp
    Rng -->|base_range| BaseRng
```

---

## 3. Диаграммы вызовов

### Фильтрация сущностей (POST /api/filter/{domain_type})

```mermaid
sequenceDiagram
    autonumber
    actor User as Клиент
    participant Flask as Flask Router
    participant Storage as storage_manager
    participant Dto as filter_dto
    participant Proto as prototype
    participant Cloned as prototype clone
    participant Worker as convert_factory

    User->>Flask: POST /api/filter/{domain_type}
    activate Flask

    Flask->>Storage: resolve_category(domain_type)
    activate Storage
    Storage-->>Flask: category
    deactivate Storage

    alt Неизвестный тип
        Flask-->>User: 400 Bad Request
    else Тип найден
        Flask->>Dto: from_dict(payload)
        Flask->>Storage: data[category]
        Storage-->>Flask: items
        Flask->>Proto: prototype(items)
        Flask->>Proto: clone(filter_dto)
        activate Cloned
        Proto-->>Flask: cloned
        Flask->>Worker: serialize(cloned.data)
        Worker-->>Flask: json
        Flask-->>User: 200 OK
        deactivate Cloned
    end
    deactivate Flask
```

### Формирование ОСВ (POST /api/osv)

```mermaid
sequenceDiagram
    autonumber
    actor User as Клиент
    participant Flask as Flask Router
    participant Storage as storage_manager
    participant Dto as filter_dto
    participant ProtoTx as prototype transactions
    participant ProtoFiltered as prototype filtered
    participant ProtoOsv as prototype osv

    User->>Flask: POST /api/osv
    activate Flask

    Flask->>Dto: from_dict(payload)
    Flask->>Storage: data[transaction_key]
    Storage-->>Flask: transactions
    Flask->>ProtoTx: prototype(transactions)
    Flask->>ProtoTx: clone(filter_dto)
    activate ProtoFiltered
    ProtoTx-->>Flask: filtered
    Flask->>ProtoFiltered: create_osv()
    activate ProtoOsv
    ProtoFiltered-->>Flask: osv
    deactivate ProtoFiltered

    Flask->>Flask: to_dict
    Flask-->>User: 200 OK
    deactivate ProtoOsv
    deactivate Flask
```

---

## 4. Как работает фильтрация и почему поля не захардкожены

1. **Нет жестких списков полей в коде:**
   - DTO фильтрации один для всех сущностей. В нем нет списков разрешенных полей.
   - Если передать поле через точку (например, `base_range.name` или `rows.nomenclature.name`), метод `_resolve_nested_path` сам достает значение из вложенных объектов или списков. Если в модели переименуют свойство, фильтрация не сломается.
   - Если передать просто `name`, то значение проверяется как в самом объекте, так и во всех связанных объектах через `references()`.

2. **Работа с любыми полями и числами:**
   - Можно фильтровать по любым полям модели, включая `value` (коэффициент пересчета), `conversion_factor` и т.д.
   - В `is_match` поддержано сравнение чисел: если пришло число или строка с числом, они сравниваются как числа.


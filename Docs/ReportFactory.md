# Архитектура подсистемы отчетов (Abstract Factory & Template Method)

Подсистема отчетов предназначена для выгрузки данных предметной области (`recipe_model`, `nomenclature_model`, `range_model`) в различных форматах представления данных в соответствии с принципами **SOLID** и шаблонами GoF.

---

## 1. Диаграмма классов (UML Class Diagram)

```mermaid
classDiagram
    direction TB

    class abstract_report_factory {
        <<abstract>>
        +create(format_type) abstract_report*
        +create_default() abstract_report*
    }

    class report_factory {
        -settings_model _settings
        +create(format_type) abstract_report
        +create_default() abstract_report
    }

    class report_type_dto {
        <<enumeration>>
        +CSV : str
        +MARKDOWN : str
        +XML : str
        +HTML : str
        +TXT : str
        +from_any(val)$ report_type_dto
    }

    class response_format_dto {
        <<enumeration>>
        +CSV : int
        +MARKDOWN : int
        +JSON : int
        +XML : int
        +TXT : int
        +HTML : int
        +RTF : int
        +YAML : int
    }

    class abstract_report {
        <<abstract>>
        -bool __is_binary
        +is_binary: bool
        +build(source) report_result_dto
        #_extract_card_fields(source)$ tuple
        #_render_recipe(source, headers, rows)* str
        #_render_card(title, xml_root, fields)* str
    }

    class csv_report {
        #_render_recipe(source, headers, rows) str
        #_render_card(title, xml_root, fields) str
    }

    class markdown_report {
        #_render_recipe(source, headers, rows) str
        #_render_card(title, xml_root, fields) str
    }

    class xml_report {
        #_render_recipe(source, headers, rows) str
        #_render_card(title, xml_root, fields) str
    }

    class html_report {
        #_render_recipe(source, headers, rows) str
        #_render_card(title, xml_root, fields) str
    }

    class text_report {
        #_render_recipe(source, headers, rows) str
        #_render_card(title, xml_root, fields) str
    }

    class report_result_dto {
        +str text
        +list binary
    }

    class settings_model {
        -response_format_dto __response_format
        +response_format: response_format_dto
    }

    abstract_report_factory <|-- report_factory : implements
    abstract_report <|-- csv_report : extends
    abstract_report <|-- markdown_report : extends
    abstract_report <|-- xml_report : extends
    abstract_report <|-- html_report : extends
    abstract_report <|-- text_report : extends

    report_factory ..> abstract_report : creates
    report_factory o-- settings_model : uses for default
    report_factory ..> report_type_dto : parses
    settings_model o-- response_format_dto : holds default
    abstract_report ..> report_result_dto : returns
```

---

## 2. Диаграмма последовательности (UML Sequence Diagram: REST API)

Показывает путь выполнения запроса к HTTP эндпоинту отчета:

```mermaid
sequenceDiagram
    autonumber
    actor User as Клиент [Браузер / F12]
    participant Flask as Flask Router [main.py]
    participant Storage as storage_manager
    participant Factory as report_factory
    participant Settings as settings_model
    participant Report as abstract_report
    participant Result as report_result_dto

    User->>Flask: GET запрос отчета
    Flask->>Storage: find_entity
    Storage-->>Flask: Объект сущности (рецепт / номенклатура / единица)

    alt Формат указан явно в URL
        Flask->>Factory: create(format_name)
    else Запрос по умолчанию
        Flask->>Factory: create_default()
        Factory->>Settings: чтение response_format
        Settings-->>Factory: response_format_dto
    end

    Factory-->>Flask: Экземпляр отчета

    Flask->>Report: build(entity)
    Note over Report: Шаблонный метод build:<br/>1. Извлечение полей<br/>2. Рендеринг данных<br/>3. Упаковка в report_result_dto
    Report-->>Flask: report_result_dto

    Flask->>Flask: format_response
    Note over Flask: Выбор MIME-типа и заголовков ответа

    alt Текстовый формат
        Flask-->>User: 200 OK - Отображение в браузере
    else Бинарный файл
        Flask-->>User: 200 OK - Скачивание файла
    end
```

---

## 3. Сводная таблица форматов отчетов

| Формат | Класс отчета | Тип данных | Content-Type | Поведение в браузере |
|---|---|---|---|---|
| **HTML** | `html_report` | Текст | `text/html; charset=utf-8` | Отображение сырой таблицы прямо на странице |
| **XML** | `xml_report` | Текст | `application/xml; charset=utf-8` | Отображение интерактивного дерева тегов XML |
| **TXT** | `text_report` | Текст | `text/plain; charset=utf-8` | Отображение плоского неформатированного текста |
| **CSV** | `csv_report` | Бинарный | `text/csv; charset=utf-8` | Скачивание файла с разделителем `;` (Excel) |
| **Markdown**| `markdown_report` | Бинарный | `text/markdown; charset=utf-8` | Скачивание файла `.md` с табличной разметкой |

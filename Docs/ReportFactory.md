# Архитектура подсистемы отчетов (Abstract Factory & Template Method)

Подсистема отчетов предназначена для выгрузки данных рецептов (`recipe_model`) в различных форматах представления данных в соответствии с принципами **SOLID** и шаблонами GoF (**Abstract Factory** и **Template Method**).

---

## 1. Диаграмма классов (UML Class Diagram)

```mermaid
classDiagram
    direction TB

    class abstract_report_factory {
        <<abstract>>
        +create(report_type) abstract_report*
        +create_default() abstract_report*
    }

    class report_factory {
        -settings_model _settings
        +create(report_type) abstract_report
        +create_default() abstract_report
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

    class settings_manager {
        +convert_report_type(val)$ report_type_enum
    }

    class abstract_report {
        <<abstract>>
        +is_binary: bool
        +mime_type: str
        +extension: str
        +build(source: recipe_model) report_result_dto
        +build_header(source: recipe_model)* str
        +build_body(source: recipe_model)* str
        +build_footer(source: recipe_model)* str
        #_combine(header, body, footer) str
    }

    class csv_report {
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class markdown_report {
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class xml_report {
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class html_report {
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class text_report {
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class rtf_report {
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class report_result_dto {
        +str text
        +list binary
    }

    class settings_model {
        -report_type_enum __response_format
        +response_format: report_type_enum
    }

    abstract_report_factory <|-- report_factory : implements
    abstract_report <|-- csv_report : extends
    abstract_report <|-- markdown_report : extends
    abstract_report <|-- xml_report : extends
    abstract_report <|-- html_report : extends
    abstract_report <|-- text_report : extends
    abstract_report <|-- rtf_report : extends

    report_factory ..> abstract_report : creates
    report_factory o-- settings_model : uses for default
    report_factory ..> settings_manager : delegates parsing to
    settings_manager ..> report_type_enum : resolves
    settings_model o-- report_type_enum : holds default
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
    Flask->>Storage: find_recipe
    Storage-->>Flask: Объект recipe_model

    alt Формат указан явно в URL / query
        Flask->>Factory: create(format_name)
    else Запрос по умолчанию
        Flask->>Factory: create_default()
        Factory->>Settings: чтение response_format
        Settings-->>Factory: report_type_enum
    end

    Factory-->>Flask: Экземпляр отчета (abstract_report)

    Flask->>Report: build(recipe)
    Note over Report: Шаблонный метод build:<br/>1. build_header(recipe)<br/>2. build_body(recipe)<br/>3. build_footer(recipe)<br/>4. Упаковка в report_result_dto
    Report-->>Flask: report_result_dto

    Flask->>Flask: format_response(report, result)
    Note over Flask: Использование свойств отчета:<br/>report.mime_type, report.extension, result.binary

    alt Текстовый формат (HTML, XML, TXT)
        Flask-->>User: 200 OK - Отображение в браузере
    else Бинарный файл (CSV, Markdown, RTF)
        Flask-->>User: 200 OK - Content-Disposition attachment (Скачивание файла)
    end
```

---

## 3. Сводная таблица форматов отчетов

| Формат | Класс отчета | Тип данных | Content-Type | Поведение в браузере |
|---|---|---|---|---|
| **HTML** | `html_report` | Текст | `text/html; charset=utf-8` | Отображение таблицы прямо на странице |
| **XML** | `xml_report` | Текст | `application/xml; charset=utf-8` | Отображение интерактивного дерева тегов XML |
| **TXT** | `text_report` | Текст | `text/plain; charset=utf-8` | Отображение неформатированного текста |
| **CSV** | `csv_report` | Бинарный | `text/csv` | Скачивание файла с разделителем `;` (Excel) |
| **Markdown**| `markdown_report` | Бинарный | `text/markdown` | Скачивание файла `.md` с табличной разметкой |
| **RTF** | `rtf_report` | Бинарный | `application/rtf` | Скачивание файла `.rtf` (WordPad, MS Word) |

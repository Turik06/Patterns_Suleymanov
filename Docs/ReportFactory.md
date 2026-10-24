# Подсистема отчетов (ReportFactory)

## 1. Диаграмма классов

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
        +is_binary: bool [property]*
        +mime_type: str [property]*
        +extension: str [property]*
        +build(source: abstract_model) report_result_dto
        +build_header(source: abstract_model)* str
        +build_body(source: abstract_model)* str
        +build_footer(source: abstract_model)* str
        +get_entity_label(source)$ str
        +get_entity_tag(source)$ str
        +get_headers(source)$ list
        +get_rows(source)$ list
        #_combine(header, body, footer) str
    }

    class csv_report {
        +is_binary: bool [property]
        +mime_type: str [property]
        +extension: str [property]
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class markdown_report {
        +is_binary: bool [property]
        +mime_type: str [property]
        +extension: str [property]
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class xml_report {
        +is_binary: bool [property]
        +mime_type: str [property]
        +extension: str [property]
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class html_report {
        +is_binary: bool [property]
        +mime_type: str [property]
        +extension: str [property]
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class text_report {
        +is_binary: bool [property]
        +mime_type: str [property]
        +extension: str [property]
        +build_header(source) str
        +build_body(source) str
        +build_footer(source) str
    }

    class rtf_report {
        +is_binary: bool [property]
        +mime_type: str [property]
        +extension: str [property]
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

## 2. Диаграмма последовательности (REST API)

```mermaid
sequenceDiagram
    autonumber
    actor User as Клиент
    participant Flask as Flask Router
    participant Storage as storage_manager
    participant Factory as report_factory
    participant Settings as settings_model
    participant Report as abstract_report

    User->>Flask: GET запрос отчета (тип, код, формат)
    Flask->>Storage: find_entity(entity_type, entity_id)
    Storage-->>Flask: Экземпляр сущности

    alt Формат указан явно в URL
        Flask->>Factory: create(format_name)
    else Запрос по умолчанию
        Flask->>Factory: create_default()
        Factory->>Settings: чтение response_format
        Settings-->>Factory: report_type_enum
    end

    Factory-->>Flask: Экземпляр отчета

    Flask->>Report: build(entity)
    Note over Report: Шаблонный метод сборки отчета
    Report-->>Flask: report_result_dto

    Flask->>Flask: format_response(report, result)

    alt Текстовый формат
        Flask-->>User: 200 OK (отображение в браузере)
    else Бинарный файл
        Flask-->>User: 200 OK (скачивание файла)
    end
```

---

## 3. Таблица форматов

| Формат | Класс отчета | Тип данных | Content-Type | Поведение |
|---|---|---|---|---|
| **HTML** | `html_report` | Текст | `text/html; charset=utf-8` | Отображение таблицы на странице |
| **XML** | `xml_report` | Текст | `application/xml; charset=utf-8` | Дерево тегов XML |
| **TXT** | `text_report` | Текст | `text/plain; charset=utf-8` | Простой текст |
| **CSV** | `csv_report` | Бинарный | `text/csv` | Скачивание файла с разделителем `;` |
| **Markdown**| `markdown_report` | Бинарный | `text/markdown` | Скачивание файла `.md` |
| **RTF** | `rtf_report` | Бинарный | `application/rtf` | Скачивание файла `.rtf` |

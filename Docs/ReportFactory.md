# Архитектура подсистемы отчетов (Abstract Factory & Template Method)

Подсистема отчетов предназначена для универсальной выгрузки данных доменных сущностей (`recipe_model`, `nomenclature_model`, `range_model` и др.) в различных форматах представления данных в соответствии с принципами **SOLID** и шаблонами GoF (**Abstract Factory** и **Template Method**).

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

## 2. Диаграмма последовательности (UML Sequence Diagram: REST API)

Показывает жизненный цикл выполнения запроса к HTTP эндпоинту отчета с полной обработкой успешных путей (**200 OK**) и ошибок (**400 Bad Request**, **404 Not Found**):

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Клиент [Браузер / API]
    participant Flask as Flask Router [main.py]
    participant Storage as storage_manager
    participant Factory as report_factory
    participant Settings as settings_model
    participant Report as abstract_report
    participant Result as report_result_dto

    User->>Flask: GET /api/report/{type}/{id}?format={fmt}
    activate Flask

    Flask->>Storage: resolve_category(type)
    activate Storage
    Storage-->>Flask: category (или None)
    deactivate Storage

    alt Неизвестная категория сущности
        Flask-->>User: 🔴 400 Bad Request (JSON {"error": "Неизвестный тип сущности"})
    else Категория найдена
        Flask->>Storage: get_by_type_and_id(type, id)
        activate Storage
        Storage-->>Flask: entity (или None)
        deactivate Storage

        alt Сущность с указанным ID не найдена
            Flask-->>User: 🔴 404 Not Found (JSON {"error": "Сущность не найдена"})
        else Сущность найдена
            alt Формат указан явно в URL / query
                Flask->>Factory: create(format_name, type)
            else Запрос по умолчанию (/api/report/default/...)
                Flask->>Factory: create_default(type)
                Factory->>Settings: чтение response_format
                Settings-->>Factory: report_type_enum
            end

            alt Некорректный формат отчета
                Factory-->>Flask: argument_exception
                Flask-->>User: 🔴 400 Bad Request (JSON {"error": "Некорректный формат отчета"})
            else Фабрика вернула экземпляр отчета
                activate Factory
                Factory-->>Flask: Экземпляр отчета (abstract_report)
                deactivate Factory

                Flask->>Report: build(entity)
                activate Report
                Note over Report: Шаблонный метод build:<br/>1. build_header(entity)<br/>2. build_body(entity)<br/>3. build_footer(entity)<br/>4. Упаковка в report_result_dto
                Report-->>Flask: report_result_dto
                deactivate Report

                Flask->>Report: create_response(result_dto, file_name)
                activate Report
                Report-->>Flask: HTTP Response
                deactivate Report

                alt Текстовый формат (HTML, XML, TXT)
                    Flask-->>User: 🟢 200 OK - Отображение в браузере (Inline)
                else Бинарный / Табличный файл (CSV, Markdown, RTF)
                    Flask-->>User: 🟢 200 OK - Content-Disposition attachment (Скачивание файла)
                end
            end
        end
    end
    deactivate Flask
```

> Полная спецификация сценариев взаимодействия и матрицы кодов ответа доступна в отдельном документе: [Диаграммы последовательности (SequenceDiagrams.md)](./SequenceDiagrams.md).

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

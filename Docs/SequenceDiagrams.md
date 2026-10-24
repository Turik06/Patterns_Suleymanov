# Диаграммы последовательности (SequenceDiagrams)

## 1. Запрос отчета через REST API

Жизненный цикл запроса к эндпоинту отчета (`GET /api/report/{type}/{id}?format={fmt}`):

```mermaid
sequenceDiagram
    autonumber
    actor User as Клиент
    participant Flask as Flask Router
    participant Storage as storage_manager
    participant Factory as report_factory
    participant Settings as settings_model
    participant Report as abstract_report

    User->>Flask: GET /api/report/{type}/{id}?format={fmt}
    activate Flask

    Flask->>Storage: resolve_category(type)
    activate Storage
    Storage-->>Flask: category
    deactivate Storage

    alt Неизвестная категория
        Flask-->>User: 400 Bad Request
    else Категория найдена
        Flask->>Storage: get_by_type_and_id(type, id)
        activate Storage
        Storage-->>Flask: entity
        deactivate Storage

        alt Объект не найден
            Flask-->>User: 404 Not Found
        else Объект найден
            alt Формат указан явно
                Flask->>Factory: create(format, type)
            else Запрос по умолчанию
                Flask->>Factory: create_default(type)
                Factory->>Settings: чтение формата
                Settings-->>Factory: format
            end

            alt Неподдерживаемый формат
                Flask-->>User: 400 Bad Request
            else Экземпляр отчета создан
                activate Factory
                Factory-->>Flask: report
                deactivate Factory

                Flask->>Report: build(entity)
                activate Report
                Note over Report: Сборка заголовка, тела и подвала
                Report-->>Flask: result_dto
                deactivate Report

                Flask->>Report: create_response(result_dto, file_name)
                activate Report
                Report-->>Flask: response
                deactivate Report

                Flask-->>User: 200 OK (данные отчета или файл)
            end
        end
    end
    deactivate Flask
```

---

## 2. Сериализация составной модели в JSON

Схема работы `convert_factory` и `reference_convertor` при обходе объекта с вложенной моделью:

```mermaid
sequenceDiagram
    autonumber
    actor User as Клиент
    participant Factory as convert_factory
    participant RefConv as reference_convertor
    participant Model as abstract_model
    participant Inner as Вложенная модель

    User->>Factory: to_json(model)
    activate Factory

    Factory->>Factory: serialize(model)
    Factory->>RefConv: convert("", model)
    activate RefConv

    RefConv->>Model: Чтение свойств модели
    Model-->>RefConv: Значения свойств и вложенная модель

    RefConv->>Factory: serialize(sub_item)
    activate Factory
    Factory->>RefConv: convert("", inner_model)
    activate RefConv
    RefConv->>Inner: Чтение свойств модели
    Inner-->>RefConv: Значения свойств
    RefConv-->>Factory: Словарь вложенной модели
    deactivate RefConv
    Factory-->>RefConv: Словарь вложенной модели
    deactivate Factory

    RefConv-->>Factory: Итоговый словарь
    deactivate RefConv

    Factory->>Factory: Формирование строки JSON
    Factory-->>User: JSON-строка
    deactivate Factory
```

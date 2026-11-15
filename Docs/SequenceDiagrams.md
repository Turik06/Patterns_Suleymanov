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

---

## 3. Управление сущностями через REST API и entity_service

### 3.1. Создание сущности (`POST /api/entity/{type}`)

```mermaid
sequenceDiagram
    autonumber
    actor User as Клиент
    participant Flask as Flask Router
    participant Service as entity_service
    participant Worker as convertor
    participant Mapping as mapping_factory
    participant Storage as storage_manager

    User->>Flask: POST /api/entity/{type} (JSON)
    activate Flask

    Flask->>Service: create_entity(type, payload, worker)
    activate Service

    Service->>Storage: resolve_category(type)
    activate Storage
    Storage-->>Service: category
    deactivate Storage

    Service->>Worker: resolve_dto(payload, type_hint=type)
    activate Worker
    Worker-->>Service: dto
    deactivate Worker

    Service->>Mapping: to_model(dto, resolver)
    activate Mapping
    Mapping-->>Service: model
    deactivate Mapping

    Service->>Service: validate_dependencies_exist(dto, model)
    alt Зависимости отсутствуют / не найдены
        Service-->>Flask: raise ValueError(ошибка валидации)
        Flask-->>User: 400 Bad Request
    else Зависимости корректны
        Service->>Service: Проверка уникальности model.unique_code
        alt Код уже существует
            Service-->>Flask: raise ValueError(дубликат)
            Flask-->>User: 400 Bad Request
        else Уникальный код
            Service->>Storage: save_entity(model)
            activate Storage
            Storage-->>Service: True
            deactivate Storage

            Service-->>Flask: model
            deactivate Service

            Flask->>Worker: serialize(model)
            activate Worker
            Worker-->>Flask: serialized_data
            deactivate Worker

            Flask-->>User: 201 Created (JSON сущности)
        end
    end
    deactivate Flask
```

### 3.2. Удаление сущности с защитой ссылочной целостности (`DELETE /api/entity/{type}/{code}`)

```mermaid
sequenceDiagram
    autonumber
    actor User as Клиент
    participant Flask as Flask Router
    participant Service as entity_service
    participant Storage as storage_manager

    User->>Flask: DELETE /api/entity/{type}/{code}
    activate Flask

    Flask->>Service: delete_entity(type, code)
    activate Service

    Service->>Storage: get_catalog(type)
    activate Storage
    Storage-->>Service: catalog
    deactivate Storage

    Service->>Service: catalog.get(code)
    alt Сущность не найдена
        Service-->>Flask: raise LookupError
        Flask-->>User: 404 Not Found
    else Сущность найдена
        Service->>Service: is_linked(code) / find_referrers(code)
        alt Есть ссылающиеся объекты
            Service-->>Flask: raise PermissionError(сообщение, referrers)
            Flask-->>User: 409 Conflict (список referrers)
        else Нет внешних ссылок
            Service->>Storage: delete_entity(type, code)
            activate Storage
            Storage->>Storage: del catalog[code]
            Storage-->>Service: True
            deactivate Storage

            Service-->>Flask: True
            deactivate Service

            Flask-->>User: 200 OK {"result": "success", "deleted": code}
        end
    end
    deactivate Flask
```

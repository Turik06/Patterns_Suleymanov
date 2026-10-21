# Диаграммы последовательности (UML Sequence Diagrams)

Данный документ содержит исчерпывающие диаграммы взаимодействия компонентов системы во времени (**UML Sequence Diagrams**) с участием акторов (**Actor / Пользователь**), демонстрирующие как успешные пути исполнения (**Happy Path: 200 OK**), так и обработку исключительных ситуаций (**Error Handling: 400 Bad Request, 404 Not Found**).

---

## 1. Жизненный цикл запроса отчета (REST API Report Generation)

Диаграмма иллюстрирует взаимодействие компонентов при обработке маршрутов `/api/report/<entity>/<id>` и `/api/report/default/<entity>/<id>`.

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Пользователь / Клиент
    participant Flask as Flask Router (main.py)
    participant Storage as storage_manager
    participant Factory as report_factory
    participant Settings as settings_model
    participant Report as abstract_report
    participant Dto as report_result_dto

    User->>Flask: GET /api/report/{type}/{id}?format={fmt}
    activate Flask

    %% 1. Проверка категории сущности
    Flask->>Storage: resolve_category(type)
    activate Storage
    Storage-->>Flask: category (или None)
    deactivate Storage

    alt Категория не найдена в хранилище
        Flask-->>User: 🔴 400 Bad Request (JSON {"error": "Неизвестный тип сущности"})
    else Категория существует
        %% 2. Поиск объекта по идентификатору
        Flask->>Storage: get_by_type_and_id(type, id)
        activate Storage
        Storage-->>Flask: entity (или None)
        deactivate Storage

        alt Сущность с указанным ID не найдена
            Flask-->>User: 🔴 404 Not Found (JSON {"error": "Сущность не найдена"})
        else Сущность успешно найдена
            %% 3. Определение формата отчета
            alt Формат указан явно в URL / Query
                Flask->>Factory: create(format_enum, type)
            else Запрос к эндпоинту /api/report/default
                Flask->>Factory: create_default(type)
                Factory->>Settings: чтение response_format
                Settings-->>Factory: report_type_enum
            end

            alt Некорректный / неподдерживаемый формат
                Factory-->>Flask: Исключение argument_exception
                Flask-->>User: 🔴 400 Bad Request (JSON {"error": "Некорректный формат отчета"})
            else Фабрика успешно вернула экземпляр отчета
                activate Factory
                Factory-->>Flask: report (наследник abstract_report)
                deactivate Factory

                %% 4. Построение отчета (Template Method)
                Flask->>Report: build(entity)
                activate Report
                Note over Report: Шаблонный метод build:<br/>1. build_header(entity)<br/>2. build_body(entity)<br/>3. build_footer(entity)
                Report-->>Flask: result_dto (report_result_dto)
                deactivate Report

                %% 5. Формирование HTTP-ответа
                Flask->>Report: create_response(result_dto, file_name)
                activate Report
                Report-->>Flask: Response (headers, mime_type, content)
                deactivate Report

                alt Текстовый отчет (HTML, XML, TXT)
                    Flask-->>User: 🟢 200 OK (Content-Type: text/..., отображение в окне)
                else Бинарный / Табличный отчет (CSV, Markdown, RTF)
                    Flask-->>User: 🟢 200 OK (Content-Disposition: attachment, скачивание)
                end
            end
        end
    end
    deactivate Flask
```

---

## 2. Жизненный цикл сериализации в JSON (REST API JSON Dump)

Диаграмма иллюстрирует процесс выгрузки данных хранилища или отдельной модели в структурированный JSON через фабрику сериализации `convert_factory`.

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Пользователь / API Клиент
    participant Flask as Flask Router (main.py)
    participant Storage as storage_manager
    participant Factory as convert_factory
    participant RefConv as reference_convertor
    participant BaseConv as basic_convertor
    participant DateConv as datetime_convertor

    User->>Flask: GET /api/dump/json (или /api/storage/{category}/json)
    activate Flask

    Flask->>Storage: Получение данных (data / category)
    activate Storage
    Storage-->>Flask: dict / domain_model
    deactivate Storage

    alt Запрошена неизвестная категория
        Flask-->>User: 🔴 400 Bad Request (JSON {"error": "Категория не найдена"})
    else Данные успешно получены
        Flask->>Factory: to_json(obj, indent=2)
        activate Factory

        Factory->>Factory: serialize(obj, visited)

        alt Простой тип (int, float, str, bool, None)
            Factory->>BaseConv: convert("", value)
            BaseConv-->>Factory: примитивное значение
        else Дата и время (datetime, date)
            Factory->>DateConv: convert("", value)
            DateConv-->>Factory: ISO-8601 строка
        else Доменная модель (abstract_model)
            Factory->>RefConv: convert("", model)
            activate RefConv
            Note over RefConv: Рекурсивный обход свойств модели<br/>с проверкой visited_ids
            RefConv-->>Factory: вложенный словарь dict
            deactivate RefConv
        end

        Factory->>Factory: json.dumps(serialized_dict, ensure_ascii=False)
        Factory-->>Flask: Строка JSON
        deactivate Factory

        Flask-->>User: 🟢 200 OK (Content-Type: application/json)
    end
    deactivate Flask
```

---

## 3. Рекурсивный процесс сериализации модели (Deep Dive Sequence)

Диаграмма показывает внутреннюю механику рекурсивного спуска фабрики `convert_factory` и конвертера `reference_convertor` для сложных моделей (рецепты с полуфабрикатами и единицы измерения с цепочкой базовых мер):

```mermaid
sequenceDiagram
    autonumber
    participant Client as Клиентский код / Тест
    participant Factory as convert_factory
    participant RefConv as reference_convertor
    participant Model as recipe_model / range_model
    participant SubModel as sub_recipe / base_range

    Client->>Factory: serialize(model)
    activate Factory

    Factory->>Factory: Регистрация id(model) в visited

    Factory->>RefConv: _convert_model(model, visited)
    activate RefConv

    RefConv->>Model: Интроспекция свойств (@property)
    activate Model
    Model-->>RefConv: {name, portions, rows / base_range, ...}
    deactivate Model

    loop Для каждого свойства модели
        alt Простое свойство (число, строка)
            RefConv->>Factory: serialize(primitive, visited)
            Factory-->>RefConv: значение
        else Вложенная доменная модель (base_range / sub_recipe)
            alt id(SubModel) уже содержится в visited (Цикл!)
                RefConv->>RefConv: Возврат {"id": id, "name": name} (Разрыв цикла)
            else Новый вложенный объект
                RefConv->>Factory: serialize(SubModel, visited)
                activate Factory
                Note over Factory,SubModel: РЕКУРСИВНЫЙ СПУСК
                Factory->>RefConv: _convert_model(SubModel, visited)
                RefConv-->>Factory: вложенный словарь dict
                Factory-->>RefConv: вложенный словарь dict
                deactivate Factory
            end
        end
    end

    RefConv-->>Factory: Итоговый сформированный словарь
    deactivate RefConv

    Factory-->>Client: dict (готов к json.dumps)
    deactivate Factory
```

---

## 4. Сводная матрица HTTP-статусов API

| HTTP Статус | Название | Причина возврата | Формат ответа |
| :--- | :--- | :--- | :--- |
| **`200 OK`** | Успех (текстовый) | Отчет в формате HTML, XML или TXT сформирован корректно | `text/html`, `application/xml`, `text/plain` |
| **`200 OK`** | Успех (скачивание) | Отчет в формате CSV, Markdown или RTF сформирован корректно | Файл во вложении (`Content-Disposition: attachment`) |
| **`200 OK`** | Успех (JSON) | Сериализация хранилища или сущности выполнена успешно | `application/json; charset=utf-8` |
| **`400 Bad Request`** | Ошибка клиента | Неизвестный тип сущности (`category`), либо недопустимый формат отчета | JSON: `{"error": "Описание ошибки"}` |
| **`404 Not Found`** | Не найдено | Сущность с указанным кодом/идентификатором отсутствует в хранилище | JSON: `{"error": "Сущность ... не найдена"}` |
| **`500 Internal Error`** | Ошибка сервера | Необработанное исключение при построении отчета или сериализации | JSON: `{"error": "Внутренняя ошибка сервера"}` |

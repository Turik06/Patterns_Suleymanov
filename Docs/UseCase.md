# Варианты использования (UseCase)

## 1. Диаграмма прецедентов

```mermaid
flowchart LR
    User[Клиент / Внешний API]
    Admin[Администратор]
    Technologist[Технолог / Шеф-повар]

    subgraph System [Система]
        direction TB

        subgraph Reports [Отчеты]
            UC1[Сформировать отчет по типу и ID]
            UC2[Сформировать отчет по умолчанию]
        end

        subgraph Serialization [Сериализация JSON]
            UC3[Выгрузить все хранилище в JSON]
            UC4[Выгрузить отдельную модель в JSON]
        end

        subgraph Recipes [Рецепты]
            UC5[Рассчитать вес брутто и нетто]
            UC6[Добавить полуфабрикат в рецепт]
        end

        subgraph AdminGroup [Управление]
            UC7[Инициализация данных first_start]
            UC8[Загрузка настроек settings.json]
        end
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4

    Technologist --> UC5
    Technologist --> UC6

    Admin --> UC7
    Admin --> UC8
```

---

## 2. Описание ролей

* **Клиент / Внешний API:** запрашивает аналитические отчеты в нужных форматах (HTML, CSV, XML, TXT, MD, RTF) или получает дампы сущностей в JSON.
* **Технолог / Шеф-повар:** настраивает рецепты, включает полуфабрикаты (составные рецепты) и контролирует расчет веса брутто и нетто.
* **Администратор:** отвечает за первичный запуск системы (`first_start()`) и файл настроек `settings.json`.

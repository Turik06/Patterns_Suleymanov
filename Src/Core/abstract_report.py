from abc import ABC, abstractmethod
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.abstract_model import abstract_model


class abstract_report(ABC):
    """
    Базовый абстрактный класс отчетов.
    Реализует шаблон проектирования "Шаблонный метод" (Template Method).
    Алгоритм формирования отчета разбит на шаги:
      1. Сформировать заголовок (build_header)
      2. Сформировать табличную часть (build_body)
      3. Сформировать подвал (build_footer)
    Поддерживает полиморфное формирование отчетов для любых доменных сущностей (abstract_model).
    """

    @property
    @abstractmethod
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        pass

    @property
    @abstractmethod
    def mime_type(self) -> str:
        """MIME-тип для HTTP ответа."""
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        """Расширение файла отчета."""
        pass

    def build(self, source: abstract_model) -> report_result_dto:
        """
        Шаблонный метод формирования отчета.
        Проверяет источник данных и последовательно выполняет:
        - формирование заголовка
        - формирование табличной части
        - формирование подвала
        """
        if source is None:
            raise argument_exception("source", "Источник данных не может быть пустым!")
        validator.validate(source, abstract_model)

        header = self.build_header(source)
        body = self.build_body(source)
        footer = self.build_footer(source)

        content = self._combine(header, body, footer)

        result = report_result_dto()
        if self.is_binary:
            result.binary = list(content.encode("utf-8"))
        else:
            result.text = content
        return result

    def _combine(self, header: str, body: str, footer: str) -> str:
        """Объединение шагов отчета в итоговый контент."""
        parts = [p for p in (header, body, footer) if p]
        return "\n".join(parts)

    @abstractmethod
    def build_header(self, source: abstract_model) -> str:
        """
        Сформировать заголовок отчета.
        """
        pass

    @abstractmethod
    def build_body(self, source: abstract_model) -> str:
        """
        Сформировать табличную часть отчета.
        """
        pass

    @abstractmethod
    def build_footer(self, source: abstract_model) -> str:
        """
        Сформировать подвал отчета.
        """
        pass

    # Словарь человекочитаемых названий сущностей для слоя отчетов
    _ENTITY_LABELS: dict[str, str] = {
        "recipe_model": "Рецепт",
        "receipt_model": "Рецепт",
        "nomenclature_model": "Номенклатура",
        "range_model": "Единица измерения",
        "storage_model": "Склад",
        "organization_model": "Организация",
        "nomenclature_group_model": "Группа номенклатуры",
        "group_model": "Группа",
    }

    # Схемы колонок и извлечения данных для простых доменных моделей
    _SIMPLE_SCHEMAS: dict[str, dict] = {
        "nomenclature_model": {
            "headers": ["Код", "Наименование", "Полное наименование", "Группа", "Единица измерения"],
            "row_extractor": lambda s: [
                str(getattr(s, "unique_code", getattr(s, "id", ""))),
                str(getattr(s, "name", "")),
                str(getattr(s, "full_name", "") or getattr(s, "name", "")),
                str(s.group.name) if getattr(s, "group", None) else "",
                str(s.range.name) if getattr(s, "range", None) else "",
            ],
            "fields_extractor": lambda s: {
                "full_name": str(getattr(s, "full_name", "") or getattr(s, "name", "")),
                "group": str(s.group.name) if getattr(s, "group", None) else "",
                "range": str(s.range.name) if getattr(s, "range", None) else "",
            },
        },
        "range_model": {
            "headers": ["Код", "Наименование", "Коэффициент", "Базовая единица"],
            "row_extractor": lambda s: [
                str(getattr(s, "unique_code", getattr(s, "id", ""))),
                str(getattr(s, "name", "")),
                str(getattr(s, "conversion_factor", 1)),
                str(s.base_range.name) if getattr(s, "base_range", None) else "базовая",
            ],
            "fields_extractor": lambda s: {
                "conversion_factor": str(getattr(s, "conversion_factor", 1)),
                "base_range": str(s.base_range.name) if getattr(s, "base_range", None) else "",
            },
        },
    }

    @classmethod
    def is_aggregate(cls, source: abstract_model) -> bool:
        """Флаг наличия вложенных табличных элементов (доменная модель-агрегат с состоянием)."""
        return hasattr(source, "items") and isinstance(getattr(source, "items", None), (list, tuple))

    @classmethod
    def get_items(cls, source: abstract_model) -> list:
        """Получить вложенные элементы агрегата."""
        return list(getattr(source, "items", []))

    @classmethod
    def get_entity_label(cls, source: abstract_model) -> str:
        """Человекочитаемое наименование типа сущности."""
        class_name = getattr(source, "__class__", type(source)).__name__.lower()
        if class_name in cls._ENTITY_LABELS:
            return cls._ENTITY_LABELS[class_name]
        return class_name.replace("_model", "").capitalize()

    @classmethod
    def get_entity_tag(cls, source: abstract_model) -> str:
        """XML/HTML тег типа сущности."""
        raw_name = getattr(source, "__class__", type(source)).__name__.lower()
        tag = raw_name.replace("_model", "")
        if tag == "receipt":
            tag = "recipe"
        return tag

    @classmethod
    def get_headers(cls, source: abstract_model) -> list[str]:
        """Заголовки таблицы отчета для переданной сущности."""
        if cls.is_aggregate(source):
            return ["Код", "Наименование", "Брутто", "Нетто"]

        class_name = getattr(source, "__class__", type(source)).__name__.lower()
        if class_name in cls._SIMPLE_SCHEMAS:
            return cls._SIMPLE_SCHEMAS[class_name]["headers"]

        return ["Код", "Наименование"]

    @classmethod
    def get_rows(cls, source: abstract_model) -> list[list[str]]:
        """Строки таблицы отчета для переданной сущности."""
        if cls.is_aggregate(source):
            return [
                [
                    str(getattr(item, "unique_code", getattr(item, "id", ""))),
                    str(getattr(item, "name", "")),
                    str(getattr(item, "brutto", 0)),
                    str(getattr(item, "netto", 0)),
                ]
                for item in getattr(source, "items", [])
            ]

        class_name = getattr(source, "__class__", type(source)).__name__.lower()
        if class_name in cls._SIMPLE_SCHEMAS:
            return [cls._SIMPLE_SCHEMAS[class_name]["row_extractor"](source)]

        return [[
            str(getattr(source, "unique_code", getattr(source, "id", ""))),
            str(getattr(source, "name", "")),
        ]]

    @classmethod
    def get_fields_dict(cls, source: abstract_model) -> dict[str, str]:
        """Словарь дополнительных полей сущности для XML и структурированных представлений."""
        class_name = getattr(source, "__class__", type(source)).__name__.lower()
        if class_name in cls._SIMPLE_SCHEMAS:
            return cls._SIMPLE_SCHEMAS[class_name]["fields_extractor"](source)

        # Динамическое извлечение полей для любых новых моделей без изменения отчетов (OCP)
        from Src.Core.common import common
        fields = {}
        for prop in common.get_fields(source, is_common=True):
            if prop not in ("id", "name", "unique_code"):
                val = getattr(source, prop, None)
                if hasattr(val, "name"):
                    val = val.name
                if val is not None:
                    fields[prop] = str(val)
        return fields


AbstractReport = abstract_report
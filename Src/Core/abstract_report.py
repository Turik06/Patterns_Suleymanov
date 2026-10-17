from abc import ABC, abstractmethod
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.abstract_model import abstract_model
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class abstract_report(ABC):
    """
    Базовый абстрактный класс отчетов.
    Реализует шаблон проектирования "Шаблонный метод" (Template Method).
    Алгоритм формирования отчета разбит на шаги:
      1. Сформировать заголовок (build_header)
      2. Сформировать табличную часть (build_body)
      3. Сформировать подвал (build_footer)
    Поддерживает формирование отчетов по любым доменным сущностям (Рецепт, Номенклатура, Единица измерения).
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

    @classmethod
    def get_entity_label(cls, source: abstract_model) -> str:
        """Человекочитаемое наименование типа сущности на русском языке."""
        if isinstance(source, recipe_model) or hasattr(source, "items"):
            return "Рецепт"
        if isinstance(source, nomenclature_model) or (hasattr(source, "group") and hasattr(source, "range")):
            return "Номенклатура"
        if isinstance(source, range_model) or hasattr(source, "conversion_factor"):
            return "Единица измерения"
        return getattr(source, "__class__", type(source)).__name__

    @classmethod
    def get_entity_tag(cls, source: abstract_model) -> str:
        """XML/HTML тег типа сущности."""
        if isinstance(source, recipe_model) or hasattr(source, "items"):
            return "recipe"
        if isinstance(source, nomenclature_model) or (hasattr(source, "group") and hasattr(source, "range")):
            return "nomenclature"
        if isinstance(source, range_model) or hasattr(source, "conversion_factor"):
            return "range"
        return getattr(source, "__class__", type(source)).__name__.lower()

    @classmethod
    def get_headers(cls, source: abstract_model) -> list[str]:
        """Универсальные заголовки таблицы отчета для переданной сущности."""
        if isinstance(source, recipe_model) or hasattr(source, "items"):
            return ["Код", "Наименование", "Брутто", "Нетто"]
        if isinstance(source, nomenclature_model) or (hasattr(source, "group") and hasattr(source, "range")):
            return ["Код", "Наименование", "Полное наименование", "Группа", "Единица измерения"]
        if isinstance(source, range_model) or hasattr(source, "conversion_factor"):
            return ["Код", "Наименование", "Коэффициент", "Базовая единица"]
        return ["Код", "Наименование"]

    @classmethod
    def get_rows(cls, source: abstract_model) -> list[list[str]]:
        """Универсальные строки таблицы отчета для переданной сущности."""
        if isinstance(source, recipe_model) or hasattr(source, "items"):
            return [
                [
                    str(getattr(item, "unique_code", getattr(item, "id", ""))),
                    str(getattr(item, "name", "")),
                    str(getattr(item, "brutto", 0)),
                    str(getattr(item, "netto", 0)),
                ]
                for item in source.items
            ]
        if isinstance(source, nomenclature_model) or (hasattr(source, "group") and hasattr(source, "range")):
            code = str(getattr(source, "unique_code", getattr(source, "id", "")))
            name = str(getattr(source, "name", ""))
            full_name = str(getattr(source, "full_name", "") or name)
            group_name = str(source.group.name) if getattr(source, "group", None) else ""
            range_name = str(source.range.name) if getattr(source, "range", None) else ""
            return [[code, name, full_name, group_name, range_name]]
        if isinstance(source, range_model) or hasattr(source, "conversion_factor"):
            code = str(getattr(source, "unique_code", getattr(source, "id", "")))
            name = str(getattr(source, "name", ""))
            factor = str(getattr(source, "conversion_factor", 1))
            base_name = str(source.base_range.name) if getattr(source, "base_range", None) else "базовая"
            return [[code, name, factor, base_name]]
        code = str(getattr(source, "unique_code", getattr(source, "id", "")))
        name = str(getattr(source, "name", ""))
        return [[code, name]]


AbstractReport = abstract_report
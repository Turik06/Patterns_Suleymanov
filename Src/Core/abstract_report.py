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

    @classmethod
    def get_entity_label(cls, source: abstract_model) -> str:
        """Человекочитаемое наименование типа сущности (делегируется модели)."""
        if hasattr(source, "get_report_title"):
            return source.get_report_title()
        return getattr(source, "__class__", type(source)).__name__

    @classmethod
    def get_entity_tag(cls, source: abstract_model) -> str:
        """XML/HTML тег типа сущности (делегируется модели)."""
        if hasattr(source, "get_report_tag"):
            return source.get_report_tag()
        return getattr(source, "__class__", type(source)).__name__.lower()

    @classmethod
    def get_headers(cls, source: abstract_model) -> list[str]:
        """Заголовки таблицы отчета для переданной сущности (делегируется модели)."""
        if hasattr(source, "get_report_headers"):
            return source.get_report_headers()
        return ["Код", "Наименование"]

    @classmethod
    def get_rows(cls, source: abstract_model) -> list[list[str]]:
        """Строки таблицы отчета для переданной сущности (делегируется модели)."""
        if hasattr(source, "get_report_rows"):
            return source.get_report_rows()
        return [[str(getattr(source, "unique_code", getattr(source, "id", ""))), str(getattr(source, "name", ""))]]


AbstractReport = abstract_report
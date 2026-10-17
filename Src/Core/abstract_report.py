from abc import ABC, abstractmethod
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model


class abstract_report(ABC):
    """
    Базовый абстрактный класс отчетов.
    Реализует шаблон проектирования "Шаблонный метод" (Template Method).
    Алгоритм формирования отчета разбит на шаги:
      1. Сформировать заголовок (build_header)
      2. Сформировать табличную часть (build_body)
      3. Сформировать подвал (build_footer)
    """

    # Флаг формата результата: True -> binary, False -> text
    is_binary: bool = False
    # MIME-тип для HTTP ответа
    mime_type: str = "text/plain"
    # Расширение файла отчета
    extension: str = "txt"

    def build(self, source: recipe_model) -> report_result_dto:
        """
        Шаблонный метод формирования отчета.
        Проверяет источник данных и последовательно выполняет:
        - формирование заголовка
        - формирование табличной части
        - формирование подвала
        """
        if source is None:
            raise argument_exception("source", "Источник данных не может быть пустым!")
        validator.validate(source, recipe_model)

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
    def build_header(self, source: recipe_model) -> str:
        """
        Сформировать заголовок отчета.
        """
        pass

    @abstractmethod
    def build_body(self, source: recipe_model) -> str:
        """
        Сформировать табличную часть отчета.
        """
        pass

    @abstractmethod
    def build_footer(self, source: recipe_model) -> str:
        """
        Сформировать подвал отчета.
        """
        pass


AbstractReport = abstract_report
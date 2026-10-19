from abc import ABC, abstractmethod
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto


class abstract_report(ABC):
    """
    Базовый абстрактный класс формирования отчетов.
    Задает единый контракт генерации отчетов (Template Method) и полиморфного формирования HTTP-ответов.
    """

    @property
    @abstractmethod
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        pass

    @property
    @abstractmethod
    def mime_type(self) -> str:
        """MIME-тип представления отчета."""
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        """Расширение файла отчета."""
        pass

    @property
    def mimetype(self) -> str:
        """MIME-тип представления отчета (алиас)."""
        return self.mime_type

    @property
    def is_attachment(self) -> bool:
        """Признак передачи отчета в виде скачиваемого вложения."""
        return self.is_binary

    @property
    def file_extension(self) -> str:
        """Расширение файла отчета (алиас)."""
        return self.extension

    def create_response(self, result: report_result_dto, filename_prefix: str = "report"):
        """
        Полиморфное построение HTTP-ответа без процедурных ветвлений.
        """
        from flask import Response
        from urllib.parse import quote

        data = bytes(result.binary) if self.is_attachment else result.text
        headers = {}
        if self.is_attachment:
            safe_name = filename_prefix.replace(" ", "_")
            encoded_name = quote(safe_name)
            headers["Content-Disposition"] = (
                f'attachment; filename="{safe_name}.{self.file_extension}"; '
                f"filename*=UTF-8''{encoded_name}.{self.file_extension}"
            )

        content_type = self.mimetype
        if not self.is_attachment and "charset" not in content_type:
            content_type = f"{content_type}; charset=utf-8"

        return Response(data, mimetype=content_type, headers=headers)

    def build(self, source: abstract_model) -> report_result_dto:
        """
        Шаблонный метод формирования отчета.
        Последовательно выполняет:
        - формирование заголовка (build_header)
        - формирование табличной части (build_body)
        - формирование подвала (build_footer)
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
        """Сформировать заголовок отчета."""
        pass

    @abstractmethod
    def build_body(self, source: abstract_model) -> str:
        """Сформировать табличную часть отчета."""
        pass

    @abstractmethod
    def build_footer(self, source: abstract_model) -> str:
        """Сформировать подвал отчета."""
        pass


AbstractReport = abstract_report
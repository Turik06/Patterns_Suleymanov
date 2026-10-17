from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model


class text_report(abstract_report):
    """Класс построения отчета в текстовом формате."""

    @property
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        return False

    @property
    def mime_type(self) -> str:
        """MIME-тип отчета."""
        return "text/plain"

    @property
    def extension(self) -> str:
        """Расширение файла отчета."""
        return "txt"

    def build_header(self, source: abstract_model) -> str:
        """Сформировать заголовок отчета."""
        return " | ".join(self.get_headers(source))

    def build_body(self, source: abstract_model) -> str:
        """Сформировать табличную часть отчета."""
        rows = self.get_rows(source)
        return "\n".join(" | ".join(row) for row in rows)

    def build_footer(self, source: abstract_model) -> str:
        """Сформировать подвал отчета."""
        return ""


TextReport = text_report
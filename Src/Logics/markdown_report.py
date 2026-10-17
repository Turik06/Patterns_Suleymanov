from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model


class markdown_report(abstract_report):
    """Класс построения отчета в формате Markdown (бинарный вывод для скачивания)."""

    @property
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        return True

    @property
    def mime_type(self) -> str:
        """MIME-тип отчета."""
        return "text/markdown"

    @property
    def extension(self) -> str:
        """Расширение файла отчета."""
        return "md"

    def build_header(self, source: abstract_model) -> str:
        """Сформировать заголовок отчета."""
        headers = self.get_headers(source)
        line = "| " + " | ".join(headers) + " |"
        sep = "| " + " | ".join(["---"] * len(headers)) + " |"
        return f"{line}\n{sep}"

    def build_body(self, source: abstract_model) -> str:
        """Сформировать табличную часть отчета."""
        rows = self.get_rows(source)
        return "\n".join("| " + " | ".join(row) + " |" for row in rows)

    def build_footer(self, source: abstract_model) -> str:
        """Сформировать подвал отчета."""
        return ""


MarkdownReport = markdown_report

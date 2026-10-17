import html
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model


class html_report(abstract_report):
    """Класс построения отчета в формате HTML."""

    @property
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        return False

    @property
    def mime_type(self) -> str:
        """MIME-тип отчета."""
        return "text/html"

    @property
    def extension(self) -> str:
        """Расширение файла отчета."""
        return "html"

    def build_header(self, source: abstract_model) -> str:
        """Сформировать заголовок отчета."""
        headers = self.get_headers(source)
        th_cells = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
        return (
            '<table border="1">\n'
            "  <thead>\n"
            f"    <tr>{th_cells}</tr>\n"
            "  </thead>\n"
            "  <tbody>"
        )

    def build_body(self, source: abstract_model) -> str:
        """Сформировать табличную часть отчета."""
        rows = self.get_rows(source)
        lines = []
        for row in rows:
            td_cells = "".join(f"<td>{html.escape(c)}</td>" for c in row)
            lines.append(f"    <tr>{td_cells}</tr>")
        return "\n".join(lines)

    def build_footer(self, source: abstract_model) -> str:
        """Сформировать подвал отчета."""
        return "  </tbody>\n</table>"


HtmlReport = html_report

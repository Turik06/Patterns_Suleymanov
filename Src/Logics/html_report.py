import html
from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model


class html_report(abstract_report):
    """Класс построения отчета в формате HTML."""

    mime_type = "text/html"
    extension = "html"
    is_binary = False

    def build_header(self, source: recipe_model) -> str:
        """Сформировать заголовок отчета."""
        return (
            '<table border="1">\n'
            "  <thead>\n"
            "    <tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr>\n"
            "  </thead>\n"
            "  <tbody>"
        )

    def build_body(self, source: recipe_model) -> str:
        """Сформировать табличную часть отчета."""
        lines = []
        for item in source.items:
            lines.append(
                f"    <tr><td>{html.escape(str(item.unique_code))}</td>"
                f"<td>{html.escape(str(item.name))}</td>"
                f"<td>{item.brutto}</td>"
                f"<td>{item.netto}</td></tr>"
            )
        return "\n".join(lines)

    def build_footer(self, source: recipe_model) -> str:
        """Сформировать подвал отчета."""
        return "  </tbody>\n</table>"


HtmlReport = html_report

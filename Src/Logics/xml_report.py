from xml.sax.saxutils import escape
from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model


class xml_report(abstract_report):
    """Класс построения отчета в формате XML (структурированный текст)."""

    mime_type = "application/xml"
    extension = "xml"
    is_binary = False

    def build_header(self, source: recipe_model) -> str:
        """Сформировать заголовок отчета."""
        return (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<recipe>\n"
            f"  <id>{escape(str(source.unique_code))}</id>\n"
            f"  <name>{escape(str(source.name))}</name>\n"
            "  <items>"
        )

    def build_body(self, source: recipe_model) -> str:
        """Сформировать табличную часть отчета."""
        lines = []
        for item in source.items:
            lines.extend([
                "    <item>",
                f"      <code>{escape(str(item.unique_code))}</code>",
                f"      <name>{escape(str(item.name))}</name>",
                f"      <brutto>{item.brutto}</brutto>",
                f"      <netto>{item.netto}</netto>",
                "    </item>",
            ])
        return "\n".join(lines)

    def build_footer(self, source: recipe_model) -> str:
        """Сформировать подвал отчета."""
        return "  </items>\n</recipe>"


XmlReport = xml_report

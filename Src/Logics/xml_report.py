from xml.sax.saxutils import escape
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model


class xml_report(abstract_report):
    """Класс построения отчета в формате XML (структурированный текст)."""

    @property
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        return False

    @property
    def mime_type(self) -> str:
        """MIME-тип отчета."""
        return "application/xml"

    @property
    def extension(self) -> str:
        """Расширение файла отчета."""
        return "xml"

    def build_header(self, source: abstract_model) -> str:
        """Сформировать заголовок отчета."""
        tag = self.get_entity_tag(source)
        header_lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f"<{tag}>",
            f"  <id>{escape(str(source.unique_code))}</id>",
            f"  <name>{escape(str(source.name))}</name>",
        ]
        if self.is_aggregate(source):
            header_lines.append("  <items>")
        return "\n".join(header_lines)

    def build_body(self, source: abstract_model) -> str:
        """Сформировать табличную часть отчета."""
        if self.is_aggregate(source):
            lines = []
            for item in self.get_items(source):
                lines.extend([
                    "    <item>",
                    f"      <code>{escape(str(getattr(item, 'unique_code', getattr(item, 'id', ''))))}</code>",
                    f"      <name>{escape(str(getattr(item, 'name', '')))}</name>",
                    f"      <brutto>{getattr(item, 'brutto', 0)}</brutto>",
                    f"      <netto>{getattr(item, 'netto', 0)}</netto>",
                    "    </item>",
                ])
            return "\n".join(lines)

        fields = self.get_fields_dict(source)
        return "\n".join(
            f"  <{key}>{escape(str(val))}</{key}>"
            for key, val in fields.items()
        )

    def build_footer(self, source: abstract_model) -> str:
        """Сформировать подвал отчета."""
        tag = self.get_entity_tag(source)
        if self.is_aggregate(source):
            return f"  </items>\n</{tag}>"
        return f"</{tag}>"



XmlReport = xml_report

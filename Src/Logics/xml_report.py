from xml.sax.saxutils import escape
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


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
        if isinstance(source, recipe_model) or hasattr(source, "items"):
            header_lines.append("  <items>")
        return "\n".join(header_lines)

    def build_body(self, source: abstract_model) -> str:
        """Сформировать табличную часть отчета."""
        if isinstance(source, recipe_model) or hasattr(source, "items"):
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
        if isinstance(source, nomenclature_model) or (hasattr(source, "group") and hasattr(source, "range")):
            full_name = getattr(source, "full_name", "") or source.name
            group_name = source.group.name if getattr(source, "group", None) else ""
            range_name = source.range.name if getattr(source, "range", None) else ""
            return "\n".join([
                f"  <full_name>{escape(str(full_name))}</full_name>",
                f"  <group>{escape(str(group_name))}</group>",
                f"  <range>{escape(str(range_name))}</range>",
            ])
        if isinstance(source, range_model) or hasattr(source, "conversion_factor"):
            factor = str(getattr(source, "conversion_factor", 1))
            base_name = source.base_range.name if getattr(source, "base_range", None) else ""
            return "\n".join([
                f"  <conversion_factor>{escape(factor)}</conversion_factor>",
                f"  <base_range>{escape(str(base_name))}</base_range>",
            ])
        return ""

    def build_footer(self, source: abstract_model) -> str:
        """Сформировать подвал отчета."""
        tag = self.get_entity_tag(source)
        if isinstance(source, recipe_model) or hasattr(source, "items"):
            return "  </items>\n</recipe>"
        return f"</{tag}>"


XmlReport = xml_report

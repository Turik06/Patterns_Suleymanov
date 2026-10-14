from xml.sax.saxutils import escape
from Src.Core.abstract_report import abstract_report


class xml_report(abstract_report):
    """Класс построения отчета в формате XML (структурированный текст)."""

    def _render_recipe(self, source, headers, rows) -> str:
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            "<recipe>",
            f"  <id>{escape(str(source.unique_code))}</id>",
            f"  <name>{escape(str(source.name))}</name>",
            "  <items>",
        ]
        for code, name, brutto, netto in rows:
            lines.extend([
                "    <item>",
                f"      <code>{escape(str(code))}</code>",
                f"      <name>{escape(str(name))}</name>",
                f"      <brutto>{brutto}</brutto>",
                f"      <netto>{netto}</netto>",
                "    </item>",
            ])
        lines.extend(["  </items>", "</recipe>"])
        return "\n".join(lines)

    def _render_card(self, title, xml_root, fields) -> str:
        lines = ['<?xml version="1.0" encoding="utf-8"?>', f"<{xml_root}>"]
        lines.extend(f"  <{tag}>{escape(str(val))}</{tag}>" for _, tag, val in fields)
        lines.append(f"</{xml_root}>")
        return "\n".join(lines)


XmlReport = xml_report

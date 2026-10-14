from Src.Core.abstract_report import abstract_report


class text_report(abstract_report):
    """Класс построения отчета в текстовом формате."""

    def _render_recipe(self, source, headers, rows) -> str:
        lines = [" | ".join(headers)]
        lines.extend(" | ".join(map(str, row)) for row in rows)
        return "\n".join(lines)

    def _render_card(self, title, xml_root, fields) -> str:
        return "\n".join(f"{label}: {val}" for label, _, val in fields)


TextReport = text_report
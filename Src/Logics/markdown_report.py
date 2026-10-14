from Src.Core.abstract_report import abstract_report


class markdown_report(abstract_report):
    """Класс построения отчета в формате Markdown (бинарный вывод для скачивания)."""
    is_binary = True

    def _render_recipe(self, source, headers, rows) -> str:
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        lines.extend("| " + " | ".join(map(str, row)) + " |" for row in rows)
        return "\n".join(lines)

    def _render_card(self, title, xml_root, fields) -> str:
        lines = [
            "| Поле | Значение |",
            "| --- | --- |",
        ]
        lines.extend(f"| {label} | {val} |" for label, _, val in fields)
        return "\n".join(lines)


MarkdownReport = markdown_report

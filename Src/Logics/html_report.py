import html
from Src.Core.abstract_report import abstract_report


class html_report(abstract_report):
    """Класс построения отчета в формате HTML (структурированный текст)."""

    @staticmethod
    def _wrap_html(doc_title: str, h1_text: str, headers: list, rows: list) -> str:
        th_cells = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '  <meta charset="utf-8">',
            f"  <title>Отчет: {html.escape(str(doc_title))}</title>",
            "  <style>",
            "    table { border-collapse: collapse; width: 100%; }",
            "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "    th { background-color: #f2f2f2; }",
            "  </style>",
            "</head>",
            "<body>",
            f"  <h1>{html.escape(str(h1_text))}</h1>",
            "  <table>",
            f"    <thead><tr>{th_cells}</tr></thead>",
            "    <tbody>",
        ]
        for row in rows:
            td_cells = "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row)
            lines.append(f"      <tr>{td_cells}</tr>")
        lines.extend(["    </tbody>", "  </table>", "</body>", "</html>"])
        return "\n".join(lines)

    def _render_recipe(self, source, headers, rows) -> str:
        return self._wrap_html(source.name, f"Рецепт: {source.name}", headers, rows)

    def _render_card(self, title, xml_root, fields) -> str:
        doc_title = title.split(": ", 1)[-1]
        rows = [(label, val) for label, _, val in fields]
        return self._wrap_html(doc_title, title, ["Поле", "Значение"], rows)


HtmlReport = html_report

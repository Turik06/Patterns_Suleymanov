import html
from Src.Core.abstract_report import abstract_report


class html_report(abstract_report):
    """Класс построения отчета в формате HTML (сырой табличный вывод)."""

    @staticmethod
    def _wrap_html(headers: list, rows: list) -> str:
        th_cells = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
        lines = [
            '<table border="1">',
            f"  <thead><tr>{th_cells}</tr></thead>",
            "  <tbody>",
        ]
        for row in rows:
            td_cells = "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row)
            lines.append(f"    <tr>{td_cells}</tr>")
        lines.extend(["  </tbody>", "</table>"])
        return "\n".join(lines)

    def _render_recipe(self, source, headers, rows) -> str:
        return self._wrap_html(headers, rows)

    def _render_card(self, title, xml_root, fields) -> str:
        rows = [(label, val) for label, _, val in fields]
        return self._wrap_html(["Поле", "Значение"], rows)


HtmlReport = html_report

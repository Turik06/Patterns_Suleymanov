from Src.Core.abstract_report import abstract_report


class csv_report(abstract_report):
    """Класс построения отчета в формате CSV (бинарный вывод для скачивания)."""
    is_binary = True

    def _render_recipe(self, source, headers, rows) -> str:
        lines = [";".join(headers)]
        lines.extend(";".join(map(str, row)) for row in rows)
        return "\n".join(lines)

    def _render_card(self, title, xml_root, fields) -> str:
        headers = ";".join(label for label, _, _ in fields)
        values = ";".join(str(val) for _, _, val in fields)
        return f"{headers}\n{values}"


CsvReport = csv_report

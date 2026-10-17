from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model


class csv_report(abstract_report):
    """Класс построения отчета в формате CSV (бинарный вывод для скачивания)."""

    is_binary = True
    mime_type = "text/csv"
    extension = "csv"

    def build_header(self, source: recipe_model) -> str:
        """Сформировать заголовок отчета."""
        return "Код;Наименование;Брутто;Нетто"

    def build_body(self, source: recipe_model) -> str:
        """Сформировать табличную часть отчета."""
        lines = [
            f"{item.unique_code};{item.name};{item.brutto};{item.netto}"
            for item in source.items
        ]
        return "\n".join(lines)

    def build_footer(self, source: recipe_model) -> str:
        """Сформировать подвал отчета."""
        return ""


CsvReport = csv_report

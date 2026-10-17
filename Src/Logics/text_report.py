from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model


class text_report(abstract_report):
    """Класс построения отчета в текстовом формате."""

    mime_type = "text/plain"
    extension = "txt"
    is_binary = False

    def build_header(self, source: recipe_model) -> str:
        """Сформировать заголовок отчета."""
        return "Код | Наименование | Брутто | Нетто"

    def build_body(self, source: recipe_model) -> str:
        """Сформировать табличную часть отчета."""
        lines = [
            f"{item.unique_code} | {item.name} | {item.brutto} | {item.netto}"
            for item in source.items
        ]
        return "\n".join(lines)

    def build_footer(self, source: recipe_model) -> str:
        """Сформировать подвал отчета."""
        return ""


TextReport = text_report
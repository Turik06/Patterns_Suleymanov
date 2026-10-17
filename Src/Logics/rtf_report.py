from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model


class rtf_report(abstract_report):
    """Класс построения отчета в формате RTF (бинарный вывод для скачивания)."""

    is_binary = True
    mime_type = "application/rtf"
    extension = "rtf"

    def build_header(self, source: recipe_model) -> str:
        """Сформировать заголовок отчета."""
        return (
            r"{\rtf1\ansi\deff0" "\n"
            r"{\fonttbl{\f0 Arial;}}" "\n"
            r"\viewkind4\uc1\pard\f0\fs20\b Рецепт: " + source.name + r"\b0\par" "\n"
            r"\b Код | Наименование | Брутто | Нетто\b0\par"
        )

    def build_body(self, source: recipe_model) -> str:
        """Сформировать табличную часть отчета."""
        lines = [
            f"{item.unique_code} | {item.name} | {item.brutto} | {item.netto}\\par"
            for item in source.items
        ]
        return "\n".join(lines)

    def build_footer(self, source: recipe_model) -> str:
        """Сформировать подвал отчета."""
        return "}"


RtfReport = rtf_report

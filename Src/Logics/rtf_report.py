from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model


class rtf_report(abstract_report):
    """Класс построения отчета в формате RTF (бинарный вывод для скачивания)."""

    @property
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        return True

    @property
    def mime_type(self) -> str:
        """MIME-тип отчета."""
        return "application/rtf"

    @property
    def extension(self) -> str:
        """Расширение файла отчета."""
        return "rtf"

    def build_header(self, source: abstract_model) -> str:
        """Сформировать заголовок отчета."""
        label = self.get_entity_label(source)
        headers = " | ".join(self.get_headers(source))
        return (
            r"{\rtf1\ansi\deff0" "\n"
            r"{\fonttbl{\f0 Arial;}}" "\n"
            rf"\viewkind4\uc1\pard\f0\fs20\b {label}: {source.name}\b0\par" "\n"
            rf"\b {headers}\b0\par"
        )

    def build_body(self, source: abstract_model) -> str:
        """Сформировать табличную часть отчета."""
        rows = self.get_rows(source)
        lines = [f"{' | '.join(row)}\\par" for row in rows]
        return "\n".join(lines)

    def build_footer(self, source: abstract_model) -> str:
        """Сформировать подвал отчета."""
        return "}"


RtfReport = rtf_report

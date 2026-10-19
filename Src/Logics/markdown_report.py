from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class markdown_report(abstract_report):
    """Базовый класс построения отчета в формате Markdown."""

    _handlers = {}

    @property
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        return True

    @property
    def mime_type(self) -> str:
        """MIME-тип отчета."""
        return "text/markdown"

    @property
    def extension(self) -> str:
        """Расширение файла отчета."""
        return "md"

    def _resolve_handler(self, source: abstract_model):
        """Поиск специализированного обработчика по типу доменной модели."""
        if type(self) is not markdown_report:
            return self

        handler_cls = self._handlers.get(type(source))
        if not handler_cls:
            for registered_type, cls_ref in self._handlers.items():
                if isinstance(source, registered_type):
                    handler_cls = cls_ref
                    break
        if not handler_cls:
            handler_cls = default_markdown_report
        return handler_cls()

    def build_header(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            return "| Код | Наименование |\n| --- | --- |"
        return handler.build_header(source)

    def build_body(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            code = getattr(source, "unique_code", getattr(source, "id", ""))
            return f"| {code} | {getattr(source, 'name', '')} |"
        return handler.build_body(source)

    def build_footer(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            return ""
        return handler.build_footer(source)

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source, abstract_model)
        handler = self._resolve_handler(source)
        if handler is not self:
            return handler.build(source)
        return super().build(source)


class recipe_markdown_report(markdown_report):
    """Построитель Markdown-отчета по технологической карте (рецепту)."""

    def build_header(self, source: recipe_model) -> str:
        return "| Код | Наименование | Брутто | Нетто |\n| --- | --- | --- | --- |"

    def build_body(self, source: recipe_model) -> str:
        lines = []
        for row in getattr(source, "items", getattr(source, "rows", [])):
            code = getattr(row, "unique_code", getattr(row, "id", ""))
            lines.append(f"| {code} | {row.name} | {row.brutto} | {row.netto} |")
        return "\n".join(lines)

    def build_footer(self, source: recipe_model) -> str:
        return ""


class nomenclature_markdown_report(markdown_report):
    """Построитель Markdown-отчета по номенклатуре."""

    def build_header(self, source: nomenclature_model) -> str:
        return "| Код | Наименование | Полное наименование | Группа | Единица измерения |\n| --- | --- | --- | --- | --- |"

    def build_body(self, source: nomenclature_model) -> str:
        code = getattr(source, "unique_code", getattr(source, "id", ""))
        full_name = getattr(source, "full_name", "") or getattr(source, "name", "")
        group_name = source.group.name if getattr(source, "group", None) else ""
        range_name = source.range.name if getattr(source, "range", None) else ""
        return f"| {code} | {source.name} | {full_name} | {group_name} | {range_name} |"

    def build_footer(self, source: nomenclature_model) -> str:
        return ""


class range_markdown_report(markdown_report):
    """Построитель Markdown-отчета по единице измерения."""

    def build_header(self, source: range_model) -> str:
        return "| Код | Наименование | Коэффициент | Базовая единица |\n| --- | --- | --- | --- |"

    def build_body(self, source: range_model) -> str:
        code = getattr(source, "unique_code", getattr(source, "id", ""))
        factor = getattr(source, "conversion_factor", 1)
        base_name = source.base_range.name if getattr(source, "base_range", None) else "базовая"
        return f"| {code} | {source.name} | {factor} | {base_name} |"

    def build_footer(self, source: range_model) -> str:
        return ""


class default_markdown_report(markdown_report):
    """Универсальный Markdown-отчет по простой модели."""

    def build_header(self, source: abstract_model) -> str:
        return "| Код | Наименование |\n| --- | --- |"

    def build_body(self, source: abstract_model) -> str:
        code = getattr(source, "unique_code", getattr(source, "id", ""))
        return f"| {code} | {getattr(source, 'name', '')} |"

    def build_footer(self, source: abstract_model) -> str:
        return ""


receipt_markdown_report = recipe_markdown_report
MarkdownReport = markdown_report

markdown_report._handlers = {
    recipe_model: recipe_markdown_report,
    nomenclature_model: nomenclature_markdown_report,
    range_model: range_markdown_report,
}

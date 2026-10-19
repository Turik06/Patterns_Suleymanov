import html
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class html_report(abstract_report):
    """Базовый класс построения отчета в формате HTML."""

    _handlers = {}

    @property
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        return False

    @property
    def mime_type(self) -> str:
        """MIME-тип отчета."""
        return "text/html"

    @property
    def extension(self) -> str:
        """Расширение файла отчета."""
        return "html"

    def _resolve_handler(self, source: abstract_model):
        """Поиск специализированного обработчика по типу доменной модели."""
        if type(self) is not html_report:
            return self

        handler_cls = self._handlers.get(type(source))
        if not handler_cls:
            for registered_type, cls_ref in self._handlers.items():
                if isinstance(source, registered_type):
                    handler_cls = cls_ref
                    break
        if not handler_cls:
            handler_cls = default_html_report
        return handler_cls()

    def build_header(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            return '<table border="1">\n  <thead>\n    <tr><th>Код</th><th>Наименование</th></tr>\n  </thead>\n  <tbody>'
        return handler.build_header(source)

    def build_body(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            code = getattr(source, "unique_code", getattr(source, "id", ""))
            return f"    <tr><td>{html.escape(str(code))}</td><td>{html.escape(str(source.name))}</td></tr>"
        return handler.build_body(source)

    def build_footer(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            return "  </tbody>\n</table>"
        return handler.build_footer(source)

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source, abstract_model)
        handler = self._resolve_handler(source)
        if handler is not self:
            return handler.build(source)
        return super().build(source)


class recipe_html_report(html_report):
    """Построитель HTML-отчета по технологической карте (рецепту)."""

    def build_header(self, source: recipe_model) -> str:
        return '<table border="1">\n  <thead>\n    <tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr>\n  </thead>\n  <tbody>'

    def build_body(self, source: recipe_model) -> str:
        lines = []
        for row in getattr(source, "items", getattr(source, "rows", [])):
            code = getattr(row, "unique_code", getattr(row, "id", ""))
            lines.append(
                f"    <tr><td>{html.escape(str(code))}</td><td>{html.escape(str(row.name))}</td><td>{row.brutto}</td><td>{row.netto}</td></tr>"
            )
        return "\n".join(lines)

    def build_footer(self, source: recipe_model) -> str:
        return "  </tbody>\n</table>"


class nomenclature_html_report(html_report):
    """Построитель HTML-отчета по номенклатуре."""

    def build_header(self, source: nomenclature_model) -> str:
        return '<table border="1">\n  <thead>\n    <tr><th>Код</th><th>Наименование</th><th>Полное наименование</th><th>Группа</th><th>Единица измерения</th></tr>\n  </thead>\n  <tbody>'

    def build_body(self, source: nomenclature_model) -> str:
        code = getattr(source, "unique_code", getattr(source, "id", ""))
        full_name = getattr(source, "full_name", "") or getattr(source, "name", "")
        group_name = source.group.name if getattr(source, "group", None) else ""
        range_name = source.range.name if getattr(source, "range", None) else ""
        return (
            f"    <tr><td>{html.escape(str(code))}</td><td>{html.escape(str(source.name))}</td>"
            f"<td>{html.escape(str(full_name))}</td><td>{html.escape(str(group_name))}</td>"
            f"<td>{html.escape(str(range_name))}</td></tr>"
        )

    def build_footer(self, source: nomenclature_model) -> str:
        return "  </tbody>\n</table>"


class range_html_report(html_report):
    """Построитель HTML-отчета по единице измерения."""

    def build_header(self, source: range_model) -> str:
        return '<table border="1">\n  <thead>\n    <tr><th>Код</th><th>Наименование</th><th>Коэффициент</th><th>Базовая единица</th></tr>\n  </thead>\n  <tbody>'

    def build_body(self, source: range_model) -> str:
        code = getattr(source, "unique_code", getattr(source, "id", ""))
        factor = getattr(source, "conversion_factor", 1)
        base_name = source.base_range.name if getattr(source, "base_range", None) else "базовая"
        return (
            f"    <tr><td>{html.escape(str(code))}</td><td>{html.escape(str(source.name))}</td>"
            f"<td>{factor}</td><td>{html.escape(str(base_name))}</td></tr>"
        )

    def build_footer(self, source: range_model) -> str:
        return "  </tbody>\n</table>"


class default_html_report(html_report):
    """Универсальный HTML-отчет по простой модели."""

    def build_header(self, source: abstract_model) -> str:
        return '<table border="1">\n  <thead>\n    <tr><th>Код</th><th>Наименование</th></tr>\n  </thead>\n  <tbody>'

    def build_body(self, source: abstract_model) -> str:
        code = getattr(source, "unique_code", getattr(source, "id", ""))
        return f"    <tr><td>{html.escape(str(code))}</td><td>{html.escape(str(source.name))}</td></tr>"

    def build_footer(self, source: abstract_model) -> str:
        return "  </tbody>\n</table>"


receipt_html_report = recipe_html_report
HtmlReport = html_report

html_report._handlers = {
    recipe_model: recipe_html_report,
    nomenclature_model: nomenclature_html_report,
    range_model: range_html_report,
}

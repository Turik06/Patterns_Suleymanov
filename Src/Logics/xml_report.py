from xml.sax.saxutils import escape
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class xml_report(abstract_report):
    """Базовый класс построения отчета в формате XML."""

    _handlers = {}

    @property
    def is_binary(self) -> bool:
        """Флаг формата результата: True -> binary, False -> text."""
        return False

    @property
    def mime_type(self) -> str:
        """MIME-тип отчета."""
        return "application/xml"

    @property
    def extension(self) -> str:
        """Расширение файла отчета."""
        return "xml"

    def _resolve_handler(self, source: abstract_model):
        """Поиск специализированного обработчика по типу доменной модели."""
        if type(self) is not xml_report:
            return self

        handler_cls = self._handlers.get(type(source))
        if not handler_cls:
            for registered_type, cls_ref in self._handlers.items():
                if isinstance(source, registered_type):
                    handler_cls = cls_ref
                    break
        if not handler_cls:
            handler_cls = default_xml_report
        return handler_cls()

    def build_header(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            tag = source.__class__.__name__.replace("_model", "")
            return f'<?xml version="1.0" encoding="utf-8"?>\n<{tag}>\n  <id>{escape(str(source.unique_code))}</id>\n  <name>{escape(str(source.name))}</name>'
        return handler.build_header(source)

    def build_body(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            return ""
        return handler.build_body(source)

    def build_footer(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            tag = source.__class__.__name__.replace("_model", "")
            return f"</{tag}>"
        return handler.build_footer(source)

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source, abstract_model)
        handler = self._resolve_handler(source)
        if handler is not self:
            return handler.build(source)
        return super().build(source)


class recipe_xml_report(xml_report):
    """Построитель XML-отчета по технологической карте (рецепту)."""

    def build_header(self, source: recipe_model) -> str:
        code = escape(str(getattr(source, "unique_code", getattr(source, "id", ""))))
        name = escape(str(source.name))
        return f'<?xml version="1.0" encoding="utf-8"?>\n<recipe>\n  <id>{code}</id>\n  <name>{name}</name>\n  <items>'

    def build_body(self, source: recipe_model) -> str:
        lines = []
        for item in getattr(source, "items", getattr(source, "rows", [])):
            item_code = escape(str(getattr(item, "unique_code", getattr(item, "id", ""))))
            item_name = escape(str(getattr(item, "name", "")))
            lines.extend([
                "    <item>",
                f"      <code>{item_code}</code>",
                f"      <name>{item_name}</name>",
                f"      <brutto>{getattr(item, 'brutto', 0)}</brutto>",
                f"      <netto>{getattr(item, 'netto', 0)}</netto>",
                "    </item>",
            ])
        return "\n".join(lines)

    def build_footer(self, source: recipe_model) -> str:
        return "  </items>\n</recipe>"


class nomenclature_xml_report(xml_report):
    """Построитель XML-отчета по номенклатуре."""

    def build_header(self, source: nomenclature_model) -> str:
        code = escape(str(getattr(source, "unique_code", getattr(source, "id", ""))))
        name = escape(str(source.name))
        return f'<?xml version="1.0" encoding="utf-8"?>\n<nomenclature>\n  <id>{code}</id>\n  <name>{name}</name>'

    def build_body(self, source: nomenclature_model) -> str:
        full_name = escape(str(getattr(source, "full_name", "") or getattr(source, "name", "")))
        group_name = escape(str(source.group.name)) if getattr(source, "group", None) else ""
        range_name = escape(str(source.range.name)) if getattr(source, "range", None) else ""
        return (
            f"  <full_name>{full_name}</full_name>\n"
            f"  <group>{group_name}</group>\n"
            f"  <range>{range_name}</range>"
        )

    def build_footer(self, source: nomenclature_model) -> str:
        return "</nomenclature>"


class range_xml_report(xml_report):
    """Построитель XML-отчета по единице измерения."""

    def build_header(self, source: range_model) -> str:
        code = escape(str(getattr(source, "unique_code", getattr(source, "id", ""))))
        name = escape(str(source.name))
        return f'<?xml version="1.0" encoding="utf-8"?>\n<range>\n  <id>{code}</id>\n  <name>{name}</name>'

    def build_body(self, source: range_model) -> str:
        factor = str(getattr(source, "conversion_factor", 1))
        base_name = escape(str(source.base_range.name)) if getattr(source, "base_range", None) else ""
        return f"  <conversion_factor>{factor}</conversion_factor>\n  <base_range>{base_name}</base_range>"

    def build_footer(self, source: range_model) -> str:
        return "</range>"


class default_xml_report(xml_report):
    """Универсальный XML-отчет по простой модели."""

    def build_header(self, source: abstract_model) -> str:
        tag = source.__class__.__name__.replace("_model", "")
        code = escape(str(getattr(source, "unique_code", getattr(source, "id", ""))))
        name = escape(str(source.name))
        return f'<?xml version="1.0" encoding="utf-8"?>\n<{tag}>\n  <id>{code}</id>\n  <name>{name}</name>'

    def build_body(self, source: abstract_model) -> str:
        return ""

    def build_footer(self, source: abstract_model) -> str:
        tag = source.__class__.__name__.replace("_model", "")
        return f"</{tag}>"


receipt_xml_report = recipe_xml_report
XmlReport = xml_report

xml_report._handlers = {
    recipe_model: recipe_xml_report,
    nomenclature_model: nomenclature_xml_report,
    range_model: range_xml_report,
}

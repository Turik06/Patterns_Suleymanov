from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class rtf_report(abstract_report):
    """Базовый класс построения отчета в формате RTF."""

    _handlers = {}

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

    def _resolve_handler(self, source: abstract_model):
        """Поиск специализированного обработчика по типу доменной модели."""
        if type(self) is not rtf_report:
            return self

        handler_cls = self._handlers.get(type(source))
        if not handler_cls:
            for registered_type, cls_ref in self._handlers.items():
                if isinstance(source, registered_type):
                    handler_cls = cls_ref
                    break
        if not handler_cls:
            handler_cls = default_rtf_report
        return handler_cls()

    def build_header(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            label = source.__class__.__name__.replace("_model", "").capitalize()
            return (
                r"{\rtf1\ansi\deff0" "\n"
                r"{\fonttbl{\f0 Arial;}}" "\n"
                rf"\viewkind4\uc1\pard\f0\fs20\b {label}: {source.name}\b0\par" "\n"
                r"\b Код | Наименование\b0\par"
            )
        return handler.build_header(source)

    def build_body(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            code = getattr(source, "unique_code", getattr(source, "id", ""))
            return rf"{code} | {getattr(source, 'name', '')}\par"
        return handler.build_body(source)

    def build_footer(self, source: abstract_model) -> str:
        handler = self._resolve_handler(source)
        if handler is self:
            return "}"
        return handler.build_footer(source)

    def build(self, source: abstract_model) -> report_result_dto:
        validator.validate(source, abstract_model)
        handler = self._resolve_handler(source)
        if handler is not self:
            return handler.build(source)
        return super().build(source)


class recipe_rtf_report(rtf_report):
    """Построитель RTF-отчета по технологической карте (рецепту)."""

    def build_header(self, source: recipe_model) -> str:
        return (
            r"{\rtf1\ansi\deff0" "\n"
            r"{\fonttbl{\f0 Arial;}}" "\n"
            rf"\viewkind4\uc1\pard\f0\fs20\b Рецепт: {source.name}\b0\par" "\n"
            r"\b Код | Наименование | Брутто | Нетто\b0\par"
        )

    def build_body(self, source: recipe_model) -> str:
        lines = []
        for item in getattr(source, "items", getattr(source, "rows", [])):
            code = getattr(item, "unique_code", getattr(item, "id", ""))
            lines.append(rf"{code} | {item.name} | {item.brutto} | {item.netto}\par")
        return "\n".join(lines)

    def build_footer(self, source: recipe_model) -> str:
        return "}"


class nomenclature_rtf_report(rtf_report):
    """Построитель RTF-отчета по номенклатуре."""

    def build_header(self, source: nomenclature_model) -> str:
        return (
            r"{\rtf1\ansi\deff0" "\n"
            r"{\fonttbl{\f0 Arial;}}" "\n"
            rf"\viewkind4\uc1\pard\f0\fs20\b Номенклатура: {source.name}\b0\par" "\n"
            r"\b Код | Наименование | Полное наименование | Группа | Единица измерения\b0\par"
        )

    def build_body(self, source: nomenclature_model) -> str:
        code = getattr(source, "unique_code", getattr(source, "id", ""))
        full_name = getattr(source, "full_name", "") or getattr(source, "name", "")
        group_name = source.group.name if getattr(source, "group", None) else ""
        range_name = source.range.name if getattr(source, "range", None) else ""
        return rf"{code} | {source.name} | {full_name} | {group_name} | {range_name}\par"

    def build_footer(self, source: nomenclature_model) -> str:
        return "}"


class range_rtf_report(rtf_report):
    """Построитель RTF-отчета по единице измерения."""

    def build_header(self, source: range_model) -> str:
        return (
            r"{\rtf1\ansi\deff0" "\n"
            r"{\fonttbl{\f0 Arial;}}" "\n"
            rf"\viewkind4\uc1\pard\f0\fs20\b Единица измерения: {source.name}\b0\par" "\n"
            r"\b Код | Наименование | Коэффициент | Базовая единица\b0\par"
        )

    def build_body(self, source: range_model) -> str:
        code = getattr(source, "unique_code", getattr(source, "id", ""))
        factor = getattr(source, "conversion_factor", 1)
        base_name = source.base_range.name if getattr(source, "base_range", None) else "базовая"
        return rf"{code} | {source.name} | {factor} | {base_name}\par"

    def build_footer(self, source: range_model) -> str:
        return "}"


class default_rtf_report(rtf_report):
    """Универсальный RTF-отчет по простой модели."""

    def build_header(self, source: abstract_model) -> str:
        label = source.__class__.__name__.replace("_model", "").capitalize()
        return (
            r"{\rtf1\ansi\deff0" "\n"
            r"{\fonttbl{\f0 Arial;}}" "\n"
            rf"\viewkind4\uc1\pard\f0\fs20\b {label}: {source.name}\b0\par" "\n"
            r"\b Код | Наименование\b0\par"
        )

    def build_body(self, source: abstract_model) -> str:
        code = getattr(source, "unique_code", getattr(source, "id", ""))
        return rf"{code} | {getattr(source, 'name', '')}\par"

    def build_footer(self, source: abstract_model) -> str:
        return "}"


receipt_rtf_report = recipe_rtf_report
RtfReport = rtf_report

rtf_report._handlers = {
    recipe_model: recipe_rtf_report,
    nomenclature_model: nomenclature_rtf_report,
    range_model: range_rtf_report,
}

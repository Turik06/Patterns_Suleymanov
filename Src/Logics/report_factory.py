from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Core.exception import argument_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Models.settings_model import settings_model
from Src.Logics.settings_manager import settings_manager
from Src.Logics.text_report import text_report
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report
from Src.Logics.rtf_report import rtf_report


class report_factory(abstract_report_factory):
    """
    Фабрика для создания отчетов на основе типа отчета или настроек.
    Инкапсулирует настройки приложения settings_model.
    """

    _settings: settings_model = None
    _mapping: dict

    def __init__(self, settings: settings_model = None):
        """Инициализация фабрики отчетов с настройками приложения."""
        if settings is None:
            s_mgr = settings_manager()
            if not s_mgr.is_loaded:
                s_mgr.load()
            settings = s_mgr.settings

        self.settings = settings
        self._mapping = {
            report_type_enum.TXT: text_report,
            report_type_enum.CSV: csv_report,
            report_type_enum.MARKDOWN: markdown_report,
            report_type_enum.XML: xml_report,
            report_type_enum.HTML: html_report,
            report_type_enum.RTF: rtf_report,
        }

    @property
    def settings(self) -> settings_model:
        """Инкапсулированные настройки приложения."""
        return self._settings

    @settings.setter
    def settings(self, value: settings_model) -> None:
        validator.validate(value, settings_model)
        self._settings = value

    def create(self, report_type, entity_type: str = "") -> abstract_report:
        """
        Создает экземпляр отчета по переданному типу.
        Делегирует разбор строковых форматов классу settings_manager.
        """
        resolved_type = (
            report_type
            if isinstance(report_type, report_type_enum)
            else settings_manager.convert_report_type(report_type)
        )
        report_cls = self._mapping.get(resolved_type)
        if report_cls is None:
            raise argument_exception("report_type", f"Указанный тип отчета '{report_type}' не реализован!")
        return report_cls()

    def create_default(self, entity_type: str = "") -> abstract_report:
        """Создает отчет по умолчанию согласно настроек."""
        if self._settings is None or not self._settings.response_format:
            return self.create(report_type_enum.HTML, entity_type)
        return self.create(self._settings.response_format, entity_type)


ReportFactory = report_factory
report_facory = report_factory

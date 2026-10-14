from Src.Core.abstract_report_factory import abstract_report_factory, AbstractReportFactory
from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Dtos.report_type_dto import report_type_dto, ReportTypeEnum
from Src.Logics.text_report import text_report, TextReport
from Src.Core.exception import argument_exception, ArgumentsException


"""
Реализация фабрики для построения отчетов
"""
class report_factory(abstract_report_factory):
    """
    Фабрика для создания и подбора отчетов на основе перечисления report_type_dto.
    """

    # Маппинг: тип отчета -> класс реализации
    _mapping: dict[report_type_dto, type[abstract_report]]

    def __init__(self):
        """
        Инициализация фабрики и регистрация сопоставлений типов отчетов с их реализациями.
        """
        self._mapping = {}
        self._mapping[report_type_dto.TXT] = text_report
        self._mapping[report_type_dto.TEXT] = text_report

    def create(self, report_type: report_type_dto) -> abstract_report:
        """
        Создает экземпляр отчета по переданному типу.
        :param report_type: Тип отчета из report_type_dto
        :return: Экземпляр соответствующего класса отчета
        :raises argument_exception: Если тип отчета не реализован или не передан
        """
        if report_type not in self._mapping:
            raise argument_exception("report_type", f"Указанный тип отчета {report_type} не реализован!")

        report_cls = self._mapping[report_type]
        return report_cls() if isinstance(report_cls, type) else report_cls


# Алиасы для соблюдения стандартов и совместимости
ReportFactory = report_factory
report_facory = report_factory

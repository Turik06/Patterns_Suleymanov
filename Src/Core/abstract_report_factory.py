from abc import ABC, abstractmethod
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_enum import report_type_enum


class abstract_report_factory(ABC):
    """
    Базовая абстрактная фабрика для создания отчетов по их типу.
    """

    @abstractmethod
    def create(self, report_type: report_type_enum) -> abstract_report:
        """
        Создать экземпляр нужного отчета по переданному типу.
        """
        pass

    @abstractmethod
    def create_default(self) -> abstract_report:
        """
        Создать экземпляр отчета по умолчанию на основе настроек.
        """
        pass


abstract_factory = abstract_report_factory
AbstractReportFactory = abstract_report_factory
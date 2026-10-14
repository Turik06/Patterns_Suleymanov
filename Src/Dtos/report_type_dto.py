from enum import Enum


"""
Типы отчетов
"""
class report_type_dto(Enum):
    """
    Перечисление поддерживаемых типов отчетов.
    """

    """
    Текстовый формат
    """
    TXT = 1
    TEXT = 1


ReportTypeEnum = report_type_dto
report_type_enum = report_type_dto
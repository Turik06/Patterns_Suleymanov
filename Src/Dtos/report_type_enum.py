from enum import Enum

"""
Типы отчетов
"""
class report_type_enum(Enum):
    """
    Перечисление поддерживаемых типов отчетов.
    """
    TXT = 1
    CSV = 2
    MARKDOWN = 3
    XML = 4
    HTML = 5
    RTF = 6

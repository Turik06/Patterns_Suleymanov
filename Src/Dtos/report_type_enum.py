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

    @classmethod
    def from_string(cls, value):
        """
        Преобразование строкового или числового представления в элемент перечисления.
        """
        from Src.Logics.settings_manager import settings_manager
        return settings_manager.convert_report_type(value)

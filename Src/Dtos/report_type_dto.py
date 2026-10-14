from enum import Enum
from Src.Core.exception import argument_exception


"""
Типы отчетов
"""
class report_type_dto(Enum):
    """
    Перечисление поддерживаемых типов отчетов.
    """
    TXT = 1
    TEXT = 1
    CSV = 2
    MARKDOWN = 3
    MD = 3
    XML = 4
    HTML = 5

    @classmethod
    def from_any(cls, value) -> "report_type_dto":
        """
        Универсальное приведение значения, строки или другого Enum к report_type_dto.
        """
        if value is None:
            raise argument_exception("report_type", "Тип отчета не может быть пустым!")
        if isinstance(value, cls):
            return value

        candidates = [value]
        if hasattr(value, "name"):
            candidates.append(value.name)
        if hasattr(value, "value"):
            candidates.append(value.value)

        for item in candidates:
            # 1. По числовому значению (например, 1, 2 или "1", "2")
            if isinstance(item, int) or (isinstance(item, str) and item.strip().isdigit()):
                try:
                    return cls(int(item))
                except ValueError:
                    pass

            # 2. По имени с учетом алиасов TXT/TEXT и MARKDOWN/MD
            key = str(item).strip().upper()
            if key in cls.__members__:
                return cls.__members__[key]

        raise argument_exception("report_type", f"Указанный тип отчета '{value}' не реализован!")


ReportTypeEnum = report_type_dto
report_type_enum = report_type_dto
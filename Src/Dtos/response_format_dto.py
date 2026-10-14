from enum import Enum


"""
Перечисление поддерживаемых форматов ответа
"""
class response_format_dto(Enum):
    """
    Перечисление форматов формирования отчетов.
    """
    CSV = "csv"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"
    TXT = "txt"
    HTML = "html"
    RTF = "rtf"
    YAML = "yaml"


ResponseFormatEnum = response_format_dto

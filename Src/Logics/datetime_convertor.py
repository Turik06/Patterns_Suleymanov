from datetime import date, datetime
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class datetime_convertor(abstract_convertor):
    """
    Конвертер объектов даты и времени в формат словаря.
    Преобразует объекты datetime.datetime и datetime.date в строковый формат ISO 8601.
    """

    def convert(self, field: str, obj: Any) -> dict:
        """
        Преобразует объект даты/времени в словарь вида {field: iso_str}.

        Параметры:
            field: Наименование поля (непустая строка)
            obj: Объект datetime или date

        Исключения:
            argument_exception: Если field не является непустой строкой
                                или тип obj не является datetime/date

        Возвращает:
            dict: {field: obj.isoformat()}
        """
        if field is None or not isinstance(field, str):
            raise argument_exception("field", "Наименование поля должно быть строкой")

        field = field.strip()
        if not field:
            raise argument_exception("field", "Наименование поля не может быть пустым")

        if not isinstance(obj, (datetime, date)):
            raise argument_exception(
                "obj",
                f"Неподдерживаемый тип для datetime_convertor: {type(obj).__name__}"
            )

        return {field: obj.isoformat()}

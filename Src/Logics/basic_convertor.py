from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class basic_convertor(abstract_convertor):
    """
    Конвертер базовых (примитивных) типов данных в формат словаря.
    Поддерживает числовые типы (int, float), строки (str), логический тип (bool) и None.
    """

    def convert(self, field: str, obj: Any) -> dict:
        """
        Преобразует примитивное значение в словарь вида {field: obj}.

        Параметры:
            field: Наименование поля (непустая строка)
            obj: Примитивное значение (int, float, str, bool, None)

        Исключения:
            argument_exception: Если field не является непустой строкой
                                или тип obj не поддерживается базовым конвертером

        Возвращает:
            dict: {field: obj}
        """
        if field is None or not isinstance(field, str):
            raise argument_exception("field", "Наименование поля должно быть строкой")

        field = field.strip()
        if not field:
            raise argument_exception("field", "Наименование поля не может быть пустым")

        if not isinstance(obj, (int, float, str, bool)) and obj is not None:
            raise argument_exception(
                "obj",
                f"Неподдерживаемый тип для basic_convertor: {type(obj).__name__}"
            )

        return {field: obj}

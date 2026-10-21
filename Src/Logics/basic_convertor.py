from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


_UNSET = object()


class basic_convertor(abstract_convertor):
    """
    Конвертер базовых (примитивных) типов данных в формат словаря.
    Поддерживает числовые типы (int, float), строки (str), логический тип (bool) и None.
    """

    def convert(self, field: Any, obj: Any = _UNSET) -> dict:
        """
        Преобразует примитивное значение в словарь вида {field: obj}.

        Параметры:
            field: Наименование поля (непустая строка) или само примитивное значение при одном аргументе
            obj: Примитивное значение (int, float, str, bool, None)

        Исключения:
            argument_exception: Если field не является непустой строкой
                                или тип obj не поддерживается базовым конвертером

        Возвращает:
            dict: {field: obj}
        """
        # Случай вызова с одним аргументом: conv.convert(10)
        if obj is _UNSET:
            val = field
            if not isinstance(val, (int, float, str, bool)) and val is not None:
                raise argument_exception(
                    "obj",
                    f"Неподдерживаемый тип для basic_convertor: {type(val).__name__}"
                )
            return {"value": val}

        # Вызов с двумя аргументами: conv.convert("count", 10)
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


BasicConvertor = basic_convertor

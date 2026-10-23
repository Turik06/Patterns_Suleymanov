from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.common import common
from Src.Core.exception import argument_exception


_UNSET = object()


class basic_convertor(abstract_convertor):
    """
    Конвертер базовых (примитивных) типов данных в формат словаря.
    Поддерживает числовые типы (int, float), строки (str), логический тип (bool) и None.
    При передаче составного объекта извлекает словарь его числовых и строковых свойств.
    """

    # Служебные свойства и псевдонимы, исключаемые из сериализации
    _IGNORED_PROPERTIES = {
        "unique_code",
        "base",
        "coefficient",
        "value",
        "items",
    }

    def convert(self, field: Any, obj: Any = _UNSET) -> dict:
        """
        Преобразует примитивное значение в словарь вида {field: obj}
        или извлекает числовые и строковые свойства из переданного объекта.

        Параметры:
            field: Наименование поля (непустая строка) или само значение/объект при одном аргументе
            obj: Примитивное значение (int, float, str, bool, None)

        Исключения:
            argument_exception: Если field не является непустой строкой (при двух аргументах)
                                или тип obj/field не поддерживается базовым конвертером

        Возвращает:
            dict: {field: obj} либо словарь свойств {prop_name: prop_value}
        """
        # Случай вызова с одним аргументом: conv.convert(target)
        if obj is _UNSET:
            val = field

            # Поддержка примитивных типов: conv.convert(10) -> {"value": 10}
            if isinstance(val, (int, float, str, bool)) or val is None:
                return {"value": val}

            # Если передан составной объект (модель или класс с @property):
            # извлекаем числовые, строковые и логические свойства
            try:
                fields = common.get_fields(val)
            except Exception:
                fields = []

            if fields:
                result = {}
                for prop_name in fields:
                    if prop_name.startswith("_") or prop_name in self._IGNORED_PROPERTIES:
                        continue
                    try:
                        prop_val = getattr(val, prop_name)
                    except Exception:
                        continue
                    if isinstance(prop_val, (int, float, str, bool)) and prop_val is not None:
                        result[prop_name] = prop_val
                return result

            raise argument_exception(
                "obj",
                f"Неподдерживаемый тип для basic_convertor: {type(val).__name__}"
            )

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

from datetime import date, datetime
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.common import common
from Src.Core.exception import argument_exception


_UNSET = object()


class datetime_convertor(abstract_convertor):
    """
    Конвертер объектов даты и времени в формат словаря.
    Преобразует объекты datetime.datetime и datetime.date в строковый формат ISO 8601.
    При передаче составного объекта извлекает словарь его полей даты и времени.
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
        Преобразует объект даты/времени в словарь вида {field: iso_str}
        или извлекает поля даты/времени из переданного составного объекта.

        Параметры:
            field: Наименование поля (непустая строка) или объект/значение при одном аргументе
            obj: Объект datetime или date

        Исключения:
            argument_exception: Если field не является непустой строкой
                                или тип obj не является datetime/date

        Возвращает:
            dict: {field: obj.isoformat()} либо словарь свойств {prop_name: iso_str}
        """
        # Случай вызова с одним аргументом: conv.convert(val)
        if obj is _UNSET:
            val = field

            # Прямая передача даты: conv.convert(dt) -> {"value": iso_str}
            if isinstance(val, (datetime, date)):
                return {"value": val.isoformat()}

            # Если передан составной объект (модель или класс с @property):
            # извлекаем свойства даты/времени
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
                    if isinstance(prop_val, (datetime, date)):
                        result[prop_name] = prop_val.isoformat()
                return result

            raise argument_exception(
                "obj",
                f"Неподдерживаемый тип для datetime_convertor: {type(val).__name__}"
            )

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

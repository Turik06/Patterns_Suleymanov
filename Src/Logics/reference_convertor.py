from datetime import date, datetime
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import abstract_model
from Src.Core.common import common
from Src.Core.exception import argument_exception


_UNSET = object()


class reference_convertor(abstract_convertor):
    """
    Конвертер ссылочных типов (доменных моделей abstract_model / name_id) в словарь.
    Рекурсивно сериализует свойства объекта и защищает от циклических ссылок.
    """

    # Псевдонимы и служебные свойства, исключаемые из сериализации во избежание дублирования
    _IGNORED_PROPERTIES = {
        "unique_code",
        "base",
        "coefficient",
        "value",
        "items",
    }

    def __init__(self, factory=None):
        """
        Инициализация конвертера ссылочных типов.

        Параметры:
            factory: Ссылка на convert_factory для делегирования сериализации вложенных полей
        """
        self._factory = factory

    @property
    def factory(self):
        """Фабрика конвертации."""
        return self._factory

    @factory.setter
    def factory(self, value):
        """Установка ссылки на фабрику."""
        self._factory = value

    def convert(self, field: Any = "", obj: Any = _UNSET) -> dict:
        """
        Преобразует доменную модель в словарь.

        Параметры:
            field: Наименование поля (строка или пустая строка/None) или сам объект при одном аргументе
            obj: Экземпляр abstract_model

        Исключения:
            argument_exception: Если field не является строкой (когда передан)
                                или obj не наследует abstract_model

        Возвращает:
            dict: {field: model_dict} если field задан, иначе model_dict
        """
        # Случай вызова с одним аргументом: conv.convert(model)
        if obj is _UNSET:
            obj = field
            field = ""

        # Поддержка перестановки аргументов conv.convert(model, "field")
        if isinstance(field, abstract_model) and isinstance(obj, str):
            field, obj = obj, field

        if field is not None and not isinstance(field, str):
            raise argument_exception("field", "Наименование поля должно быть строкой")

        if not isinstance(obj, abstract_model):
            raise argument_exception(
                "obj",
                f"Неподдерживаемый тип для reference_convertor: {type(obj).__name__}. Ожидается abstract_model"
            )

        model_dict = self._convert_model(obj, set())

        if field is not None and field.strip():
            return {field.strip(): model_dict}
        return model_dict

    def _convert_model(self, obj: abstract_model, visited: set) -> dict:
        """
        Внутренний метод извлечения свойств доменной модели в словарь.
        """
        obj_id = str(getattr(obj, "id", id(obj)))
        if obj_id in visited:
            # Защита от циклической рекурсии: возвращаем краткую ссылку
            return {
                "id": obj_id,
                "name": str(getattr(obj, "name", "")),
            }

        visited_copy = set(visited)
        visited_copy.add(obj_id)

        raw_data = {}
        try:
            fields = common.get_fields(obj)
        except Exception:
            fields = []

        for prop_name in fields:
            if prop_name.startswith("_") or prop_name in self._IGNORED_PROPERTIES:
                continue

            try:
                val = getattr(obj, prop_name)
            except Exception:
                continue

            raw_data[prop_name] = self._serialize_value(val, visited_copy)

        # Упорядочиваем: id и name первыми, остальные свойства по алфавиту
        result = {}
        if "id" in raw_data:
            result["id"] = raw_data.pop("id")
        if "name" in raw_data:
            result["name"] = raw_data.pop("name")
        for key in sorted(raw_data.keys()):
            result[key] = raw_data[key]

        return result

    def _serialize_value(self, value: Any, visited: set) -> Any:
        """
        Сериализация отдельного значения свойства (делегирование фабрике или прямой рекурсивный обход).
        """
        if self._factory is not None and hasattr(self._factory, "serialize"):
            return self._factory.serialize(value, visited)

        if isinstance(value, (int, float, str, bool)) or value is None:
            return value

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, abstract_model):
            return self._convert_model(value, visited)

        if isinstance(value, (list, tuple, set)):
            return [self._serialize_value(item, visited) for item in value]

        if isinstance(value, dict):
            return {k: self._serialize_value(v, visited) for k, v in value.items()}

        return str(value)

import json
from datetime import date, datetime
from typing import Any, Type
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import abstract_model
from Src.Core.common import common
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


_UNSET = object()


class convert_factory:
    """
    Фабрика конвертеров данных в форматы словарей и JSON.
    Реализует шаблон 'Фабрика' и типовой реестр сопоставления для исключения if-else ветвлений.
    """

    def __init__(self):
        """
        Инициализация фабрики и регистрация базовых сопоставлений типов.
        """
        self._convertors: dict[type, Type[abstract_convertor]] = {}
        self._instances: dict[Type[abstract_convertor], abstract_convertor] = {}

        # Реестр сопоставлений типов конвертерам по умолчанию
        self.register(int, basic_convertor)
        self.register(float, basic_convertor)
        self.register(str, basic_convertor)
        self.register(bool, basic_convertor)
        self.register(type(None), basic_convertor)
        self.register(datetime, datetime_convertor)
        self.register(date, datetime_convertor)
        self.register(abstract_model, reference_convertor)

    def register(self, target_type: type, convertor_cls: Type[abstract_convertor]) -> None:
        """
        Зарегистрировать класс конвертера для указанного типа данных.

        Параметры:
            target_type: Целевой тип данных (класс)
            convertor_cls: Класс конвертера (наследник abstract_convertor)
        """
        if not isinstance(target_type, type):
            raise argument_exception("target_type", "Целевой тип должен быть классом (type)")

        if not isinstance(convertor_cls, type) or not issubclass(convertor_cls, abstract_convertor):
            raise argument_exception(
                "convertor_cls",
                "Класс конвертера должен наследоваться от abstract_convertor"
            )

        self._convertors[target_type] = convertor_cls

    def _get_instance(self, convertor_cls: Type[abstract_convertor]) -> abstract_convertor:
        """Получить или создать экземпляр конвертера с передачей контекста фабрики."""
        if convertor_cls not in self._instances:
            instance = convertor_cls()
            if hasattr(instance, "factory"):
                instance.factory = self
            self._instances[convertor_cls] = instance
        return self._instances[convertor_cls]

    def get_convertor(self, obj_or_type: Any) -> abstract_convertor:
        """
        Найти и вернуть экземпляр конвертера для переданного объекта или типа.

        Параметры:
            obj_or_type: Объект данных или его класс
        """
        if obj_or_type is None:
            target_type = type(None)
        elif isinstance(obj_or_type, type):
            target_type = obj_or_type
        else:
            target_type = type(obj_or_type)

        # 1. Прямой поиск в реестре типов
        if target_type in self._convertors:
            return self._get_instance(self._convertors[target_type])

        # 2. Поиск по наследованию (issubclass)
        for registered_type, convertor_cls in self._convertors.items():
            if issubclass(target_type, registered_type):
                return self._get_instance(convertor_cls)

        raise argument_exception(
            "obj_or_type",
            f"Не найден зарегистрированный конвертер для типа: {target_type.__name__}"
        )

    def create(self, obj_or_type: Any) -> abstract_convertor:
        """
        Алиас метода get_convertor по каноническому шаблону Factory.
        """
        return self.get_convertor(obj_or_type)

    def convert(self, field: Any = "", obj: Any = _UNSET) -> Any:
        """
        Преобразовать объект в словарь вида {field: value} или выполнить сериализацию объекта.

        Параметры:
            field: Наименование поля или сам объект при одном аргументе
            obj: Объект любого поддерживаемого типа
        """
        # Случай вызова с одним аргументом: factory.convert(obj)
        if obj is _UNSET:
            return self.serialize(field)

        # Поддержка перестановки аргументов factory.convert(obj, "field")
        if not isinstance(field, str) and isinstance(obj, str):
            field, obj = obj, field

        if isinstance(obj, (list, tuple, set)):
            serialized_list = [self.serialize(item) for item in obj]
            return {field: serialized_list} if field else serialized_list

        if isinstance(obj, dict):
            serialized_dict = {str(k): self.serialize(v) for k, v in obj.items()}
            return {field: serialized_dict} if field else serialized_dict

        convertor = self.get_convertor(obj)
        return convertor.convert(field, obj)

    def serialize(self, obj: Any, visited: set = None) -> Any:
        """
        Рекурсивная сериализация любого объекта в структуры dict/list/примитивы.

        Параметры:
            obj: Исходный объект данных (доменная модель, словарь, список, примитив)
            visited: Множество уже посещенных идентификаторов (защита от циклов)
        """
        if visited is None:
            visited = set()

        if obj is None:
            return None

        if isinstance(obj, (int, float, str, bool)):
            return obj

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if isinstance(obj, abstract_model):
            conv = self.get_convertor(obj)
            if isinstance(conv, reference_convertor):
                return conv._convert_model(obj, visited)
            return conv.convert("", obj)

        if isinstance(obj, (list, tuple, set)):
            return [self.serialize(item, visited) for item in obj]

        if isinstance(obj, dict):
            return {str(k): self.serialize(v, visited) for k, v in obj.items()}

        # Проверка составного объекта со свойствами @property (например, DTO или тестовый стаб)
        try:
            fields = common.get_fields(obj)
        except Exception:
            fields = []

        if fields:
            obj_id = str(getattr(obj, "id", id(obj)))
            if obj_id in visited:
                return {"id": obj_id}
            visited_copy = set(visited)
            visited_copy.add(obj_id)

            res = {}
            for prop in fields:
                if prop.startswith("_"):
                    continue
                try:
                    val = getattr(obj, prop)
                except Exception:
                    continue
                res[prop] = self.serialize(val, visited_copy)
            return res

        try:
            conv = self.get_convertor(obj)
            return conv.convert("", obj)
        except Exception:
            return str(obj)

    def to_json(self, obj: Any, indent: int = 2) -> str:
        """
        Преобразовать объект любого типа в строку формата JSON.

        Параметры:
            obj: Доменная модель, примитив, коллекция или хранилище данных
            indent: Количество пробелов отступа (по умолчанию 2)
        """
        serialized = self.serialize(obj)
        return json.dumps(serialized, ensure_ascii=False, indent=indent)

    def dumps(self, obj: Any, indent: int = 2) -> str:
        """Алиас для to_json."""
        return self.to_json(obj, indent=indent)

    def dump(self, obj: Any, fp, indent: int = 2) -> None:
        """Выгрузка сериализованного объекта в файловый поток."""
        serialized = self.serialize(obj)
        json.dump(serialized, fp, ensure_ascii=False, indent=indent)

import json
from datetime import date, datetime
from typing import Any, Type, Dict
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import abstract_model
from Src.Core.entity_model import entity_model
from Src.Core.abstract_dto import abstract_dto
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception, argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Logics.list_convertor import list_convertor
from Src.Logics.dict_convertor import dict_convertor
from Src.Logics.domain_convertor import domain_convertor
from Src.Logics.mapping_factory import mapping_factory

_UNSET = object()


"""
Фабрика для создания конверторов
"""
class convert_factory(abstract_convert_factory):
    __mapping: Dict[Type, Any] = {}
    __mapping_factory: mapping_factory = None
    __instance = None

    def __init__(self):
        super().__init__()
        self.__mapping_factory = mapping_factory()
        self.__mapping = {
            int: basic_convertor(),
            float: basic_convertor(),
            str: basic_convertor(),
            bool: basic_convertor(),
            datetime: datetime_convertor(),
            date: datetime_convertor(),
            list: list_convertor(self, self.__mapping_factory),
            dict: dict_convertor(self, self.__mapping_factory),
            entity_model: domain_convertor(self, self.__mapping_factory),
            abstract_model: domain_convertor(self, self.__mapping_factory),
            abstract_dto: domain_convertor(self, self.__mapping_factory),
            type(None): basic_convertor(),
        }

        self._convertors: dict[type, Type[abstract_convertor]] = {}
        self._instances: dict[Type[abstract_convertor], abstract_convertor] = {}

        self.register(int, basic_convertor)
        self.register(float, basic_convertor)
        self.register(str, basic_convertor)
        self.register(bool, basic_convertor)
        self.register(type(None), basic_convertor)
        self.register(datetime, datetime_convertor)
        self.register(date, datetime_convertor)
        self.register(abstract_model, reference_convertor)

    # Синглтон
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(convert_factory, cls).__new__(cls)
        return cls.__instance

    """
    Создать нужный конвертор
    """
    def create(self, source: Any) -> abstract_convertor:
        if source is None:
            return self.__mapping[type(None)]

        for source_type, conv in self.__mapping.items():
            if isinstance(source, source_type):
                return conv

        for source_type, conv in self.__mapping.items():
            if isinstance(source, type) and issubclass(source, source_type):
                return conv

        raise operation_exception(f"Указанный тип {type(source).__name__} не поддерживается!")

    """
    Зарегистрировать класс конвертера для типа
    """
    def register(self, target_type: type, convertor_cls: Type[abstract_convertor]) -> None:
        if not isinstance(target_type, type):
            raise argument_exception("target_type", "Целевой тип должен быть классом")

        if not isinstance(convertor_cls, type) or not issubclass(convertor_cls, abstract_convertor):
            raise argument_exception(
                "convertor_cls",
                "Класс конвертера должен наследоваться от abstract_convertor"
            )

        self._convertors[target_type] = convertor_cls

    def _get_instance(self, convertor_cls: Type[abstract_convertor]) -> abstract_convertor:
        if convertor_cls not in self._instances:
            instance = convertor_cls()
            if hasattr(instance, "factory"):
                instance.factory = self
            self._instances[convertor_cls] = instance
        return self._instances[convertor_cls]

    """
    Найти конвертер для переданного объекта или типа
    """
    def get_convertor(self, obj_or_type: Any) -> abstract_convertor:
        if obj_or_type is None:
            target_type = type(None)
        elif isinstance(obj_or_type, type):
            target_type = obj_or_type
        else:
            target_type = type(obj_or_type)

        if target_type in self._convertors:
            return self._get_instance(self._convertors[target_type])

        for registered_type, convertor_cls in self._convertors.items():
            if issubclass(target_type, registered_type):
                return self._get_instance(convertor_cls)

        raise argument_exception(
            "obj_or_type",
            f"Не найден конвертер для типа: {target_type.__name__}"
        )

    """
    Преобразовать объект в словарь
    """
    def convert(self, field: Any = "", obj: Any = _UNSET) -> Any:
        if obj is _UNSET:
            return self.serialize(field)

        if not isinstance(field, str) and isinstance(obj, str):
            field, obj = obj, field

        if isinstance(obj, (list, tuple, set)):
            serialized_list = [self.serialize(item) for item in obj]
            return {field: serialized_list} if field else serialized_list

        if isinstance(obj, dict):
            serialized_dict = {str(k): self.serialize(v) for k, v in obj.items()}
            return {field: serialized_dict} if field else serialized_dict

        conv = self.get_convertor(obj)
        return conv.convert(field, obj)

    """
    Сериализация объекта в словарь или список
    """
    def serialize(self, obj: Any, visited: set = None) -> Any:
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

    """
    Преобразовать объект в строку JSON
    """
    def to_json(self, obj: Any, indent: int = 2) -> str:
        serialized = self.serialize(obj)
        return json.dumps(serialized, ensure_ascii=False, indent=indent)

    def dumps(self, obj: Any, indent: int = 2) -> str:
        return self.to_json(obj, indent=indent)

    def dump(self, obj: Any, fp, indent: int = 2) -> None:
        serialized = self.serialize(obj)
        json.dump(serialized, fp, ensure_ascii=False, indent=indent)

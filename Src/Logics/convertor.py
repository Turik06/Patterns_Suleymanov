import json
from Src.Logics.convert_factory import convert_factory
from Src.Logics.mapping_factory import mapping_factory
from Src.Core.validator import validator
from Src.Core.common import common
from Src.Core.abstract_dto import abstract_dto


class convertor:
    """Конвертор данных"""
    __factory: convert_factory = None
    __mapping_factory: mapping_factory = None
    __instance = None

    def __init__(self):
        self.__factory = convert_factory()
        self.__mapping_factory = mapping_factory()

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(convertor, cls).__new__(cls)
        return cls.__instance

    def serialize(self, source: any) -> dict:
        """Сериализовать объект в словарь"""
        conv = self.__factory.create(source)
        return conv.serialize("result", source)

    def resolve_dto(self, item: dict, type_hint: str = None):
        """Создать экземпляр DTO по данным словаря"""
        if not isinstance(item, dict):
            return None

        type_name = item.get("type") or type_hint
        if type_name:
            dto_cls = self.__mapping_factory.find_dto_by_type(type_name)
            if dto_cls:
                return dto_cls().load_dict(item)

        keys = set(item.keys())
        for dto_cls in self.__mapping_factory.mapping:
            if isinstance(dto_cls, type) and issubclass(dto_cls, abstract_dto):
                fields = set(common.get_fields(dto_cls()))
                if keys.issubset(fields):
                    return dto_cls().load_dict(item)

        return None

    def deserialize(self, source: any) -> object:
        """Десериализовать словарь в объект или хранилище"""
        if isinstance(source, str):
            source = json.loads(source)
        validator.validate(source, dict)
        data = source.get("result", source)

        is_storage = ("unique_code" not in data) and ("name" not in data) and any(
            isinstance(v, (list, dict)) for v in data.values()
        )

        if is_storage:
            dtos = {}
            storage_dtos = {}

            for key, val in data.items():
                items = list(val.values()) if isinstance(val, dict) else list(val)
                storage_dtos[key] = []
                for item in items:
                    dto = self.resolve_dto(item, type_hint=key)
                    if dto:
                        code = getattr(dto, "unique_code", "")
                        if code:
                            dtos[code] = dto
                        storage_dtos[key].append(dto)

            cache = {}

            def resolve(code: str):
                if not code:
                    return None
                if code in cache:
                    return cache[code]
                if code in dtos:
                    dto = dtos[code]
                    model = self.__mapping_factory.to_model(dto, resolve)
                    if model and code:
                        cache[code] = model
                    return model
                return None

            restored = {}
            for key, dtoList in storage_dtos.items():
                restored[key] = []
                for dto in dtoList:
                    code = getattr(dto, "unique_code", "")
                    model = resolve(code) if code else self.__mapping_factory.to_model(dto, resolve)
                    if model:
                        restored[key].append(model)

            return restored

        dto = self.resolve_dto(data)
        if dto:
            return self.__mapping_factory.to_model(dto)

        return None

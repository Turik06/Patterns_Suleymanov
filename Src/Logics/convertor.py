import json
from Src.Logics.convert_factory import convert_factory
from Src.Logics.mapping_factory import mapping_factory
from Src.Core.validator import validator
from Src.Core.common import common
from Src.Core.abstract_dto import abstract_dto


class convertor:
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

    def find_dto_type(self, item: dict):
        """Найти подходящий DTO по полям словаря"""
        if not isinstance(item, dict):
            return None

        keys = set(item.keys())
        best_cls = None
        min_diff = None

        for dto_cls in self.__mapping_factory.mapping:
            if isinstance(dto_cls, type) and issubclass(dto_cls, abstract_dto):
                fields = set(common.get_fields(dto_cls()))
                if keys.issubset(fields):
                    diff = len(fields - keys)
                    if min_diff is None or diff < min_diff:
                        min_diff = diff
                        best_cls = dto_cls

        return best_cls

    def deserialize(self, source: any) -> object:
        """Десериализовать словарь в объект или хранилище"""
        if isinstance(source, str):
            source = json.loads(source)
        validator.validate(source, dict)
        data = source.get("result", source)

        # Проверка на словарь хранилища
        is_storage = ("unique_code" not in data) and ("name" not in data) and any(
            isinstance(v, (list, dict)) for v in data.values()
        )

        if is_storage:
            cache = {}
            restored = {}

            # Порядок загрузки по зависимостям
            def sort_key(entry):
                _, v = entry
                items = list(v.values()) if isinstance(v, dict) else list(v)
                if not items or not isinstance(items[0], dict):
                    return 0
                keys = set(items[0].keys())
                if "items" in keys:
                    return 4
                if "nomenclature_code" in keys:
                    return 3
                if "group_code" in keys:
                    return 2
                if "base_code" in keys:
                    return 1
                return 0

            sorted_entries = sorted(data.items(), key=sort_key)
            all_dtos = []

            for key, val in sorted_entries:
                items = list(val.values()) if isinstance(val, dict) else list(val)
                restored[key] = []
                for item in items:
                    dto_cls = self.find_dto_type(item)
                    if dto_cls:
                        dto = dto_cls().load_dict(item)
                        all_dtos.append(dto)
                        model = self.__mapping_factory.to_model(dto, cache)
                        restored[key].append(model)

            # Связываем базовые единицы
            for dto in all_dtos:
                base_code = getattr(dto, "base_code", None)
                code = getattr(dto, "unique_code", None)
                if base_code and base_code in cache and code in cache:
                    cache[code].base = cache[base_code]

            return restored

        # Одиночный объект
        dto_cls = self.find_dto_type(data)
        if dto_cls:
            dto = dto_cls().load_dict(data)
            return self.__mapping_factory.to_model(dto)

        return None

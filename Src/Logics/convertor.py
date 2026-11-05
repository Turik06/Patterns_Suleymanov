import json
from Src.Logics.convert_factory import convert_factory
from Src.Logics.mapping_factory import mapping_factory
from Src.Logics.storage_manager import storage_manager
from Src.Core.validator import validator
from Src.Dtos.range_dto import range_dto
from Src.Dtos.nomenclature_group_dto import nomenclature_group_dto
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.storage_dto import storage_dto
from Src.Dtos.recipe_dto import recipe_dto
from Src.Dtos.recipe_row_dto import recipe_row_dto
from Src.Dtos.company_dto import company_dto


"""
Конвертор данных
"""
class convertor:
    __factory: convert_factory = None
    __mapping_factory: mapping_factory = None
    __instance = None

    def __init__(self):
        self.__factory = convert_factory()
        self.__mapping_factory = mapping_factory()

    # Синглтон
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(convertor, cls).__new__(cls)
        return cls.__instance

    """
    Сериализовать объект в словарь
    """
    def serialize(self, source: any) -> dict:
        conv = self.__factory.create(source)
        result = conv.serialize("result", source)
        return result

    """
    Десериализовать словарь в объект
    """
    def deserialize(self, source: any) -> object:
        if isinstance(source, str):
            source = json.loads(source)
        validator.validate(source, dict)
        data = source.get("result", source)

        categories = {
            storage_manager.group_key(): nomenclature_group_dto,
            storage_manager.range_key(): range_dto,
            storage_manager.storage_key(): storage_dto,
            storage_manager.nomenclature_key(): nomenclature_dto,
            storage_manager.receipt_key(): recipe_dto,
        }

        # Если передан словарь хранилища
        if any(key in data for key in categories):
            cache = {}
            restored = {}

            for key, dto_cls in categories.items():
                if key in data:
                    restored[key] = {}
                    items = data[key].values() if isinstance(data[key], dict) else data[key]
                    for item in items:
                        dto = dto_cls().load_dict(item)
                        model = self.__mapping_factory.to_model(dto, cache)
                        restored[key][model.unique_code] = model

            # Связываем базовые единицы
            range_key = storage_manager.range_key()
            if range_key in data:
                for item in (data[range_key].values() if isinstance(data[range_key], dict) else data[range_key]):
                    base_code = item.get("base_code")
                    code = item.get("unique_code")
                    if base_code and base_code in cache and code in cache:
                        cache[code].base = cache[base_code]

            return restored

        # Если передана одна модель
        single_types = [
            ("base_code", range_dto),
            ("group_code", nomenclature_dto),
            ("instructions", recipe_dto),
            ("address", storage_dto),
            ("inn", company_dto),
            ("nomenclature_code", recipe_row_dto),
        ]
        for field, dto_cls in single_types:
            if field in data:
                return self.__mapping_factory.to_model(dto_cls().load_dict(data))

        return self.__mapping_factory.to_model(nomenclature_group_dto().load_dict(data))

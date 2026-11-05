from typing import Dict, Type
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.abstract_model import abstract_model
from Src.Core.abstract_dto import abstract_dto
from Src.Dtos.range_dto import range_dto
from Src.Models.range_model import range_model
from Src.Dtos.nomenclature_group_dto import nomenclature_group_dto
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Dtos.storage_dto import storage_dto
from Src.Models.storage_model import storage_model
from Src.Dtos.recipe_row_dto import recipe_row_dto
from Src.Models.recipe_row_model import recipe_row_model
from Src.Dtos.recipe_dto import recipe_dto
from Src.Models.recipe_model import recipe_model
from Src.Dtos.company_dto import company_dto
from Src.Models.organization_model import organization_model


"""
Фабрика маппинга DTO и доменных моделей
"""
class mapping_factory(abstract_mapping_factory):
    __mapping: Dict[Type, Type] = {}
    __instance = None

    def __init__(self):
        super().__init__()
        self.__mapping = {
            range_dto: range_model,
            nomenclature_group_dto: nomenclature_group_model,
            nomenclature_dto: nomenclature_model,
            storage_dto: storage_model,
            recipe_row_dto: recipe_row_model,
            recipe_dto: recipe_model,
            company_dto: organization_model,
            int: int,
            float: float,
            bool: bool,
            str: str,
            list: list,
            dict: dict,
        }

    # Синглтон
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(mapping_factory, cls).__new__(cls)
        return cls.__instance

    """
    Сконвертировать модель в DTO
    """
    def to_dto(self, source: object) -> object:
        if source is None:
            return None

        # Если уже DTO - отдаем как есть
        if isinstance(source, abstract_dto):
            return source

        for dto_type, domain_type in self.__mapping.items():
            if isinstance(source, domain_type):
                if isinstance(source, abstract_model):
                    return dto_type().from_domain_model(source)
                return source

        return None

    """
    Создать модель из DTO
    """
    def to_model(self, source: object, cache: dict = None) -> object:
        if source is None:
            return None
        if isinstance(source, abstract_model):
            return source
        if cache is None:
            cache = {}

        code = getattr(source, "unique_code", "")
        if code and code in cache:
            return cache[code]

        if isinstance(source, range_dto):
            model = range_model(source.name, source.value)
            if source.base_code and source.base_code in cache:
                model.base = cache[source.base_code]
        elif isinstance(source, nomenclature_group_dto):
            model = nomenclature_group_model(source.name)
        elif isinstance(source, storage_dto):
            model = storage_model(source.name, source.address)
        elif isinstance(source, nomenclature_dto):
            model = nomenclature_model(source.name, source.name, cache.get(source.group_code), cache.get(source.range_code))
        elif isinstance(source, recipe_row_dto):
            model = recipe_row_model(cache.get(source.nomenclature_code), source.brutto, source.netto, cache.get(source.range_code))
        elif isinstance(source, recipe_dto):
            model = recipe_model(source.name)
            model.instructions = list(source.instructions)
            for item in (source.items or []):
                if item in cache:
                    model.add_row(cache[item])
        elif isinstance(source, company_dto):
            model = organization_model()
            model.name, model.inn, model.bic = source.name, source.inn, source.bik
        else:
            return None

        if code:
            model.unique_code = code
            cache[code] = model
        return model

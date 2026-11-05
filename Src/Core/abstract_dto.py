from abc import ABC, abstractmethod
from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator
from Src.Core.common import common


"""
Базовый класс DTO
"""
class abstract_dto(ABC):

    """
    Создать DTO из модели
    """
    @abstractmethod
    def from_domain_model(self, source: abstract_model) -> "abstract_dto":
        pass

    """
    Загрузить данные из словаря
    """
    def load_dict(self, source: dict) -> "abstract_dto":
        validator.validate(source, dict)
        for field in common.get_fields(self):
            val = source.get(field)
            if val is not None and (not isinstance(val, str) or val.strip()):
                setattr(self, field, val)
        return self

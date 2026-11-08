from abc import ABC, abstractmethod
from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator
from Src.Core.common import common


class abstract_dto(ABC):
    """Базовый класс DTO"""
    __type: str = ""

    @property
    def type(self) -> str:
        """Тип сущности"""
        return self.__type

    @type.setter
    def type(self, value: str):
        validator.validate(value, str)
        self.__type = value.strip()

    @abstractmethod
    def from_domain_model(self, source: abstract_model) -> "abstract_dto":
        """Создать DTO из модели"""
        pass

    def to_domain_model(self, resolver=None) -> abstract_model:
        """Создать модель из DTO"""
        from Src.Logics.mapping_factory import mapping_factory
        return mapping_factory().to_model(self, resolver)

    def load_dict(self, source: dict) -> "abstract_dto":
        """Загрузить данные из словаря"""
        validator.validate(source, dict)
        for field in common.get_fields(self):
            val = source.get(field)
            if val is not None and (not isinstance(val, str) or val.strip()):
                setattr(self, field, val)
        return self

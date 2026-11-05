from abc import ABC, abstractmethod
from Src.Core.abstract_model import abstract_model


"""
Базовый класс для DTO
"""
class abstract_dto(ABC):

    """
    Создать DTO из доменной модели
    """
    @abstractmethod
    def from_domain_model(self, source: abstract_model) -> "abstract_dto":
        pass

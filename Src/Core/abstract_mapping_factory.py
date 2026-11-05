from abc import ABC, abstractmethod


"""
Фабрика маппинга DTO и моделей
"""
class abstract_mapping_factory(ABC):

    """
    Перевести модель в DTO
    """
    @abstractmethod
    def to_dto(self, source: object) -> object:
        pass

    """
    Перевести DTO в модель
    """
    @abstractmethod
    def to_model(self, source: object) -> object:
        pass

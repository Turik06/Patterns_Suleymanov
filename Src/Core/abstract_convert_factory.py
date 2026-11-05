from abc import ABC, abstractmethod
from Src.Core.abstract_convertor import abstract_convertor


"""
Фабрика для создания конверторов
"""
class abstract_convert_factory(ABC):

    """
    Создать нужный конвертор
    """
    @abstractmethod
    def create(self, source: any) -> abstract_convertor:
        pass

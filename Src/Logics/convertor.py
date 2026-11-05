from Src.Logics.convert_factory import convert_factory
from Src.Core.validator import validator


"""
Конвертор данных
"""
class convertor:
    __factory: convert_factory = None
    __instance = None

    def __init__(self):
        self.__factory = convert_factory()

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
    def deserialize(self, source: dict) -> object:
        pass

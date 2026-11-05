from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.validator import validator, argument_exception


"""
Конвертация словаря
"""
class dict_convertor(abstract_convertor):
    __convert_factory: abstract_convert_factory = None
    __mapping_factory: abstract_mapping_factory = None

    def __init__(self, convert_factory: abstract_convert_factory = None, mapping_factory: abstract_mapping_factory = None):
        super().__init__()
        if convert_factory is not None:
            validator.validate(convert_factory, abstract_convert_factory)
        self.__convert_factory = convert_factory

        if mapping_factory is not None:
            validator.validate(mapping_factory, abstract_mapping_factory)
        self.__mapping_factory = mapping_factory

    """
    Сериализация словаря
    """
    def serialize(self, field: str, object: any) -> dict:
        validator.validate(field, str)
        if not isinstance(object, dict):
            raise argument_exception("object", "Ожидается словарь")

        result = {}
        for key, value in object.items():
            str_key = str(key)
            if self.__convert_factory is not None:
                convertor = self.__convert_factory.create(value)
                inner = convertor.serialize(str_key, value)
                result[str_key] = inner[str_key] if isinstance(inner, dict) and str_key in inner else inner
            else:
                result[str_key] = value

        return {field: result}

    def convert(self, field: any, obj: any = None) -> dict:
        if obj is None and not isinstance(field, str):
            obj = field
            field = "result"
        return self.serialize(str(field) if field else "result", obj)

    def deserialize(self, source: dict) -> object:
        pass

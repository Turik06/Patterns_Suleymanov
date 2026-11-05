from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.abstract_model import abstract_model
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception


"""
Конвертор доменных сущностей
"""
class domain_convertor(abstract_convertor):
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

    @property
    def factory(self) -> abstract_convert_factory:
        return self.__convert_factory

    """
    Сериализация модели через DTO
    """
    def serialize(self, field: str, object: any) -> dict:
        validator.validate(field, str)
        if object is None:
            return {field: None}

        if isinstance(object, (int, float, str, bool)):
            return {field: object}

        dto = object
        if self.__mapping_factory is not None and isinstance(object, abstract_model):
            dto = self.__mapping_factory.to_dto(object)
            if dto is None:
                raise operation_exception(f"Невозможно сопоставить тип {type(object).__name__}")

        result = {}
        fields = common.get_fields(dto)

        for item in fields:
            value = getattr(dto, item)
            value_dto = self.__mapping_factory.to_dto(value) if self.__mapping_factory is not None else value
            if value_dto is None and value is not None:
                raise operation_exception(f"Невозможно сопоставить тип {type(value).__name__}")

            if self.__convert_factory is not None:
                convertor = self.__convert_factory.create(value_dto)
                inner_result = convertor.serialize(item, value_dto)
                result[item] = inner_result[item] if isinstance(inner_result, dict) and item in inner_result else inner_result
            else:
                result[item] = value_dto

        return {field: result}

    def convert(self, field: any, obj: any = None) -> dict:
        if obj is None and not isinstance(field, str):
            obj = field
            field = "result"
        return self.serialize(str(field) if field else "result", obj)

    def deserialize(self, source: dict) -> object:
        pass

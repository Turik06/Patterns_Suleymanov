from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator, argument_exception


"""
Конвертация списка
"""
class list_convertor(abstract_convertor):
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
    Сериализация списка
    """
    def serialize(self, field: str, items: any) -> dict:
        validator.validate(field, str)
        if not isinstance(items, (list, tuple, set)):
            raise argument_exception("items", "Ожидается список")

        result = []
        for item in items:
            dto = item
            if self.__mapping_factory is not None and isinstance(item, abstract_model):
                dto = self.__mapping_factory.to_dto(item)

            if self.__convert_factory is not None:
                convertor = self.__convert_factory.create(dto)
                convert_result = convertor.serialize(field, dto)
                result.append(convert_result[field] if isinstance(convert_result, dict) and field in convert_result else convert_result)
            else:
                result.append(dto)

        return {field: result}

    def convert(self, field: any, obj: any = None) -> dict:
        if obj is None and not isinstance(field, str):
            obj = field
            field = "result"
        return self.serialize(str(field) if field else "result", obj)

    def deserialize(self, source: dict) -> object:
        pass

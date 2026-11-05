from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Dtos.nomenclature_group_dto import nomenclature_group_dto
from Src.Logics.basic_convertor import basic_convertor
from Src.Core.common import common
from Src.Logics.domain_convertor import domain_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Dtos.range_dto import range_dto
from Src.Models.range_model import range_model
from Src.Logics.convertor import convertor
from Src.Logics.mapping_factory import mapping_factory


"""
Проверить сериализацию полей nomenclature_group_dto через basic_convertor
"""
def test_group_model_basic_convertor_serialization():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    domain = manager.data[storage_manager.group_key()][0]
    dto = nomenclature_group_dto().from_domain_model(domain)
    convertor_inst = basic_convertor()
    fields = common.get_fields(dto, is_common=True)
    result = {}

    # Действие
    for field in fields:
        value = getattr(dto, field)
        result.update(convertor_inst.serialize(field, value))

    # Проверки
    assert convertor_inst.error_text == ""
    assert result["unique_code"] == domain.unique_code
    assert result["name"] == domain.name


"""
Проверить сериализацию полей range_dto через domain_convertor
"""
def test_range_model_domain_convertor_serialize():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    domain = range_model.create_kilogram()
    dto = range_dto().from_domain_model(domain)
    cn_factory = convert_factory()
    mp_factory = mapping_factory()
    convertor_inst = domain_convertor(cn_factory, mp_factory)
    fields = common.get_fields(dto, is_common=True)
    result = {}

    # Действие
    for field in fields:
        value = getattr(dto, field)
        result.update(convertor_inst.serialize(field, value))

    # Проверки
    assert convertor_inst.error_text == ""
    assert len(result) > 0


"""
Проверить сериализацию рецепта
"""
def test_receipt_model_serialize():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    domain = manager.data[storage_manager.receipt_key()][0]

    # Действие
    result = convertor().serialize(domain)

    # Проверка
    assert len(result) > 0


"""
Выполнить сериализацию всех данных
"""
def test_storage_manager_serialize():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    # Действие
    result = convertor().serialize(manager.data)

    # Проверки
    assert len(result) > 0

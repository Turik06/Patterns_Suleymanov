from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Logics.convertor import convertor
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Dtos.nomenclature_dto import nomenclature_dto


def test_deserialize_single_range():
    """Проверить десериализацию единицы измерения"""
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    orig = manager.data[storage_manager.range_key()][0]

    c = convertor()
    serialized = c.serialize(orig)
    restored = c.deserialize(serialized)

    assert isinstance(restored, range_model)
    assert restored.unique_code == orig.unique_code
    assert restored.name == orig.name
    assert restored.value == orig.value


def test_deserialize_single_recipe():
    """Проверить десериализацию рецепта"""
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    orig = manager.data[storage_manager.receipt_key()][0]

    c = convertor()
    serialized = c.serialize(orig)
    restored = c.deserialize(serialized)

    assert isinstance(restored, recipe_model)
    assert restored.unique_code == orig.unique_code
    assert restored.name == orig.name


def test_deserialize_full_storage_matches_original():
    """Проверить десериализацию всего хранилища"""
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    c = convertor()
    serialized = c.serialize(manager.data)
    restored = c.deserialize(serialized)

    for key in storage_manager.keys():
        if key in restored:
            orig_list = manager.data[key]
            assert len(restored[key]) == len(orig_list)
            orig_codes = {item.unique_code for item in orig_list}
            restored_codes = {item.unique_code for item in restored[key]}
            assert restored_codes == orig_codes

    range_key = storage_manager.range_key()
    restored_ranges = {r.unique_code: r for r in restored[range_key]}
    for orig_range in manager.data[range_key]:
        if orig_range.base is not None:
            restored_range = restored_ranges[orig_range.unique_code]
            assert restored_range.base is not None
            assert restored_range.base.unique_code == orig_range.base.unique_code

    nom_key = storage_manager.nomenclature_key()
    restored_noms = {n.unique_code: n for n in restored[nom_key]}
    for orig_nom in manager.data[nom_key]:
        assert restored_noms[orig_nom.unique_code].full_name == orig_nom.full_name


def test_deserialize_single_nomenclature_preserves_full_name():
    """Проверить, что при десериализации номенклатуры полное имя не теряется"""
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    orig = manager.data[storage_manager.nomenclature_key()][0]

    dto = nomenclature_dto().from_domain_model(orig)
    cache = {orig.group.unique_code: orig.group, orig.range.unique_code: orig.range}
    restored = dto.to_domain_model(cache)

    assert restored.unique_code == orig.unique_code
    assert restored.name == orig.name
    assert restored.full_name == orig.full_name
    assert restored.full_name != restored.name


def test_domain_model_from_dto_factory():
    """Проверить создание модели через фабричный метод from_dto"""
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    orig = manager.data[storage_manager.range_key()][0]

    from Src.Dtos.range_dto import range_dto
    dto = range_dto().from_domain_model(orig)
    restored = range_model.from_dto(dto)

    assert isinstance(restored, range_model)
    assert restored.unique_code == orig.unique_code
    assert restored.name == orig.name


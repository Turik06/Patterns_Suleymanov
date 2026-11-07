from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Logics.convertor import convertor
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


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

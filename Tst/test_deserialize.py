from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Logics.convertor import convertor
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


"""
Проверить десериализацию единицы измерения
"""
def test_deserialize_single_range():
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


"""
Проверить десериализацию рецепта
"""
def test_deserialize_single_recipe():
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


"""
Проверить десериализацию хранилища и сравнить со storage_manager
"""
def test_deserialize_full_storage_matches_original():
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    c = convertor()
    serialized = c.serialize(manager.data)
    restored = c.deserialize(serialized)

    # Проверка совпадения через метод storage_manager.keys
    for key in storage_manager.keys():
        if key in restored:
            orig_dict = manager.data[key]
            assert len(restored[key]) == len(orig_dict)
            assert set(restored[key].keys()) == set(orig_dict.keys())

    # Проверка базовой единицы
    for code, restored_range in restored[storage_manager.range_key()].items():
        orig_range = manager.data[storage_manager.range_key()][code]
        if orig_range.base is not None:
            assert restored_range.base is not None
            assert restored_range.base.unique_code == orig_range.base.unique_code

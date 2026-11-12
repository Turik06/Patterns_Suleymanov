from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Dtos.recipe_dto import recipe_dto
from Src.Dtos.range_dto import range_dto
from Src.Dtos.nomenclature_dto import nomenclature_dto


"""
Проверить получение рецепта из storage_manager
"""
def test_receipt_dto_from_storage_manager_build():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    # Действие
    domain = manager.data[storage_manager.receipt_key()][0]
    dto = recipe_dto().from_domain_model(domain)

    # Проверки
    assert dto.name == domain.name
    assert dto.brutto == domain.brutto
    assert dto.netto == domain.netto
    assert len(dto.items) == len(domain.items)


"""
Проверить получение единицы измерения из storage_manager
"""
def test_range_dto_from_storage_manager_build():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    # Действие
    domain = manager.data[storage_manager.range_key()][0]
    dto = range_dto().from_domain_model(domain)

    # Проверки
    assert dto.name == domain.name
    assert dto.value == domain.value
    if domain.base is not None:
        assert dto.base_code == domain.base.unique_code


"""
Проверить получение номенклатуры из storage_manager
"""
def test_ingredient_dto_from_storage_manager_build():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    # Действие
    domain = manager.data[storage_manager.nomenclature_key()][0]
    dto = nomenclature_dto().from_domain_model(domain)

    # Проверки
    assert dto.name == domain.name
    assert dto.full_name == domain.full_name
    assert dto.range_code == domain.range.unique_code

    # Проверка восстановления доменной модели
    restored = dto.to_domain_model({dto.range_code: domain.range, dto.group_code: domain.group})
    assert restored.name == domain.name
    assert restored.full_name == domain.full_name
    assert restored.full_name != restored.name

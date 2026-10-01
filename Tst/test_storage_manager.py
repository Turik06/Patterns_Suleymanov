import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model


"""
Набор модульных тестов для класса storage_manager
"""


# 1. Проверка шаблона Singleton


def test_singleton_storage_manager_same_instance():
    """Проверить, что два вызова возвращают один и тот же объект в памяти (is)."""
    m1 = storage_manager()
    m2 = storage_manager()
    assert m1 is m2


def test_singleton_storage_manager_equal():
    """Проверить равенство двух инстансов через оператор =="""
    m1 = storage_manager()
    m2 = storage_manager()
    assert m1 == m2


def test_singleton_storage_manager_shared_data():
    """Проверить тест с пары: данные в двух инстансах синглтона общие."""
    m1 = storage_manager()
    m1.convert()
    m2 = storage_manager()

    assert m1.ranges is m2.ranges
    assert m1.nomenclatures is m2.nomenclatures
    assert len(m1.ranges) == len(m2.ranges)


# 2. Проверка первого старта и сформированных данных


def test_storage_manager_convert_returns_true():
    """Проверить, что метод convert() возвращает True."""
    manager = storage_manager()
    assert manager.convert() == True


def test_storage_manager_is_initialized_flag():
    """Проверить, что флаг is_initialized становится True после convert()."""
    manager = storage_manager()
    manager.convert()
    assert manager.is_initialized == True


def test_first_start_storage_manager_ranges():
    """Проверить сформированные единицы измерения (5 штук, грамм, кг с коэффициентом 1000)."""
    manager = storage_manager()
    manager.convert()

    assert len(manager.ranges) == 5
    names = [r.name for r in manager.ranges.values()]
    assert "грамм" in names
    assert "килограмм" in names
    assert "литр" in names
    assert "миллилитр" in names
    assert "штука" in names

    # Проверка связи производной единицы
    kg = next(r for r in manager.ranges.values() if r.name == "килограмм")
    assert kg.conversion_factor == 1000
    assert kg.base_range is not None
    assert kg.base_range.name == "грамм"


def test_first_start_storage_manager_groups():
    """Проверить сформированные группы номенклатуры (Бакалея и Молочные продукты)."""
    manager = storage_manager()
    manager.convert()

    assert len(manager.groups) == 2
    group_names = [g.name for g in manager.groups.values()]
    assert "Бакалея" in group_names
    assert "Молочные продукты" in group_names


def test_first_start_storage_manager_nomenclatures():
    """Проверить номенклатуру под рецепт (6 ингредиентов, корректные связи)."""
    manager = storage_manager()
    manager.convert()

    assert len(manager.nomenclatures) == 6
    nom_names = [n.name for n in manager.nomenclatures.values()]
    assert "Мука пшеничная" in nom_names
    assert "Молоко 3.2%" in nom_names
    assert "Яйца куриные" in nom_names
    assert "Масло сливочное" in nom_names

    # Проверяем, что номенклатура корректно связана с объектами группы и единицы
    flour = next(n for n in manager.nomenclatures.values() if n.name == "Мука пшеничная")
    assert flour.group.name == "Бакалея"
    assert flour.range.name == "килограмм"


def test_first_start_storage_manager_storages():
    """Проверить сформированные склады (Основной склад и Холодильник цеха)."""
    manager = storage_manager()
    manager.convert()

    assert len(manager.storages) == 2
    storage_names = [s.name for s in manager.storages.values()]
    assert "Основной склад" in storage_names
    assert "Холодильник цеха" in storage_names


# 3. Проверка уникальности и валидации


def test_unique_storage_manager_duplicate_rejected():
    """Проверить, что повторное добавление существующего объекта отклоняется (уникальность по id)."""
    manager = storage_manager()
    manager.convert()

    existing_range = list(manager.ranges.values())[0]
    count_before = len(manager.ranges)

    result = manager.add_range(existing_range)
    assert result == False
    assert len(manager.ranges) == count_before


def test_unique_storage_manager_add_new_item():
    """Проверить успешное добавление новой уникальной сущности."""
    manager = storage_manager()
    manager.convert()

    count_before = len(manager.storages)
    new_storage = storage_model(name="Архивный склад", address="ул. Складская, 1")

    result = manager.add_storage(new_storage)
    assert result == True
    assert len(manager.storages) == count_before + 1


def test_storage_manager_rejects_invalid_type():
    """Проверить, что методы добавления отклоняют объекты неверного типа."""
    manager = storage_manager()
    assert manager.add_storage("не склад") == False
    assert manager.add_range(123) == False
    assert manager.add_nomenclature(None) == False
    assert manager.add_group([]) == False


def test_storage_manager_convert_idempotent():
    """Проверить идемпотентность: повторный вызов convert() не дублирует данные."""
    manager = storage_manager()
    manager.convert()

    count_ranges = len(manager.ranges)
    count_noms = len(manager.nomenclatures)

    # Повторный вызов
    result = manager.convert()
    assert result == True
    assert len(manager.ranges) == count_ranges
    assert len(manager.nomenclatures) == count_noms

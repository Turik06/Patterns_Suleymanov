import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model


"""
Набор модульных тестов для класса storage_manager
"""


# 1. Проверка шаблона Singleton


def test_same_instance_storage_manager_singleton():
    """
    Ожидание: Два вызова возвращают один и тот же объект в памяти.
    Метод: storage_manager.__new__
    Описание: Проверяет оператор is — оба инстанса ссылаются на один объект.
    """
    m1 = storage_manager()
    m2 = storage_manager()
    assert m1 is m2


def test_equal_storage_manager_singleton():
    """
    Ожидание: Два инстанса равны через оператор ==.
    Метод: storage_manager.__new__
    Описание: Проверяет равенство двух инстансов синглтона.
    """
    m1 = storage_manager()
    m2 = storage_manager()
    assert m1 == m2


def test_shared_data_storage_manager_singleton():
    """
    Ожидание: Данные в двух инстансах синглтона общие.
    Метод: storage_manager.__new__
    Описание: Тест с пары — коллекции ranges и nomenclatures ссылаются на одни объекты.
    """
    m1 = storage_manager()
    m1.convert()
    m2 = storage_manager()

    assert m1.ranges is m2.ranges
    assert m1.nomenclatures is m2.nomenclatures
    assert len(m1.ranges) == len(m2.ranges)


# 2. Проверка первого старта и сформированных данных


def test_true_storage_manager_convert():
    """
    Ожидание: convert() возвращает True.
    Метод: storage_manager.convert
    Описание: Проверяет успешность выполнения метода convert().
    """
    manager = storage_manager()
    assert manager.convert() == True


def test_true_storage_manager_is_initialized():
    """
    Ожидание: Флаг is_initialized равен True после convert().
    Метод: storage_manager.is_initialized (getter)
    Описание: После вызова convert() внутренний флаг инициализации становится True.
    """
    manager = storage_manager()
    manager.convert()
    assert manager.is_initialized == True


def test_true_storage_manager_is_loaded():
    """
    Ожидание: is_loaded возвращает True после convert().
    Метод: storage_manager.is_loaded (переопределение abstract_manager)
    Описание: Проверяет контракт базового класса abstract_manager: после успешной
              конвертации свойство is_loaded должно возвращать True.
    """
    manager = storage_manager()
    manager.convert()
    assert manager.is_loaded == True


def test_success_storage_manager_first_start_ranges():
    """
    Ожидание: Сформировано 5 единиц измерения с корректными связями.
    Метод: storage_manager.convert
    Описание: Проверяет наличие грамм, килограмм, штука, литр, миллилитр.
              Килограмм — производная от грамма с коэффициентом 1000.
    """
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


def test_success_storage_manager_first_start_groups():
    """
    Ожидание: Сформировано 3 группы номенклатуры.
    Метод: storage_manager.convert
    Описание: Проверяет наличие групп Бакалея, Молочные продукты и Блюда.
    """
    manager = storage_manager()
    manager.convert()

    assert len(manager.groups) == 3
    group_names = [g.name for g in manager.groups.values()]
    assert "Бакалея" in group_names
    assert "Молочные продукты" in group_names
    assert "Блюда" in group_names


def test_success_storage_manager_first_start_nomenclatures():
    """
    Ожидание: Сформировано 7 позиций номенклатуры с корректными связями.
    Метод: storage_manager.convert
    Описание: 6 ингредиентов для рецепта и 1 готовое блюдо (Блины классические).
              Проверяет корректные связи номенклатуры с группами и единицами.
    """
    manager = storage_manager()
    manager.convert()

    assert len(manager.nomenclatures) == 7
    nom_names = [n.name for n in manager.nomenclatures.values()]
    assert "Мука пшеничная" in nom_names
    assert "Молоко 3.2%" in nom_names
    assert "Яйца куриные" in nom_names
    assert "Масло сливочное" in nom_names
    assert "Блины классические" in nom_names

    # Проверяем связи ингредиента
    flour = next(n for n in manager.nomenclatures.values() if n.name == "Мука пшеничная")
    assert flour.group.name == "Бакалея"
    assert flour.range.name == "килограмм"

    # Проверяем связи готового блюда
    pancakes = next(n for n in manager.nomenclatures.values() if n.name == "Блины классические")
    assert pancakes.group.name == "Блюда"
    assert pancakes.range.name == "штука"


def test_success_storage_manager_first_start_storages():
    """
    Ожидание: Сформировано 2 склада.
    Метод: storage_manager.convert
    Описание: Проверяет наличие Основного склада и Холодильника цеха.
    """
    manager = storage_manager()
    manager.convert()

    assert len(manager.storages) == 2
    storage_names = [s.name for s in manager.storages.values()]
    assert "Основной склад" in storage_names
    assert "Холодильник цеха" in storage_names


# 3. Проверка уникальности и валидации


def test_false_storage_manager_add_duplicate_range():
    """
    Ожидание: Повторное добавление существующего объекта отклоняется (False).
    Метод: storage_manager.add_range
    Описание: Уникальность по id — объект с тем же id не добавляется повторно.
    """
    manager = storage_manager()
    manager.convert()

    existing_range = list(manager.ranges.values())[0]
    count_before = len(manager.ranges)

    result = manager.add_range(existing_range)
    assert result == False
    assert len(manager.ranges) == count_before


def test_true_storage_manager_add_new_storage():
    """
    Ожидание: Новая уникальная сущность успешно добавляется (True).
    Метод: storage_manager.add_storage
    Описание: Добавление нового склада с уникальным id увеличивает размер коллекции.
    """
    manager = storage_manager()
    manager.convert()

    count_before = len(manager.storages)
    new_storage = storage_model(name="Архивный склад", address="ул. Складская, 1")

    result = manager.add_storage(new_storage)
    assert result == True
    assert len(manager.storages) == count_before + 1


def test_false_storage_manager_add_invalid_type():
    """
    Ожидание: Методы добавления отклоняют объекты неверного типа (False).
    Метод: storage_manager.add_storage, add_range, add_nomenclature, add_group
    Описание: Передача строки, числа, None или списка вместо моделей возвращает False.
    """
    manager = storage_manager()
    assert manager.add_storage("не склад") == False
    assert manager.add_range(123) == False
    assert manager.add_nomenclature(None) == False
    assert manager.add_group([]) == False


def test_success_storage_manager_convert_idempotent():
    """
    Ожидание: Повторный вызов convert() не дублирует данные.
    Метод: storage_manager.convert
    Описание: Идемпотентность — второй вызов convert() возвращает True,
              но количество элементов не меняется.
    """
    manager = storage_manager()
    manager.convert()

    count_ranges = len(manager.ranges)
    count_noms = len(manager.nomenclatures)

    # Повторный вызов
    result = manager.convert()
    assert result == True
    assert len(manager.ranges) == count_ranges
    assert len(manager.nomenclatures) == count_noms


# 4. Проверка поведения при is_first_start == False


def test_empty_storage_manager_convert_is_first_start_false():
    """
    Ожидание: Пустые коллекции при is_first_start == False.
    Метод: storage_manager.convert
    Описание: Если флаг первого старта False, генерация первичных данных не выполняется,
              все коллекции остаются пустыми. convert() возвращает True.
    """
    # Сбрасываем синглтон для чистого теста
    if hasattr(storage_manager, 'instance'):
        del storage_manager.instance

    # Временно меняем флаг первого старта
    s_manager = settings_manager()
    if not s_manager.is_loaded:
        s_manager.load()
    original_value = s_manager.settings.is_first_start
    s_manager.settings.is_first_start = False

    try:
        manager = storage_manager()
        result = manager.convert()

        assert result == True
        assert len(manager.ranges) == 0
        assert len(manager.groups) == 0
        assert len(manager.nomenclatures) == 0
        assert len(manager.storages) == 0
    finally:
        # Восстанавливаем исходное состояние
        s_manager.settings.is_first_start = original_value
        if hasattr(storage_manager, 'instance'):
            del storage_manager.instance

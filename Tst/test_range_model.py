import pytest
from Src.Core.exception import argument_exception
from Src.Models.range_model import range_model


def test_success_range_model_create_base_unit():
    """
    Ожидание: Успешное создание базовой единицы измерения.
    Метод: range_model.__init__
    Описание: Базовая единица (грамм, коэффициент 1) создаётся без передачи base_range.
              Свойство base_range должно быть None.
    """
    # Arrange & Act (Подготовка и Действие)
    gram = range_model("грамм", 1)

    # Assert (Проверка)
    assert gram.name == "грамм"
    assert gram.conversion_factor == 1
    assert gram.base_range is None
    assert gram.base is None


def test_success_range_model_create_derived_unit():
    """
    Ожидание: Успешное создание производной единицы измерения.
    Метод: range_model.__init__
    Описание: Производная единица (кг, коэффициент 1000) создаётся со ссылкой на базовую единицу (грамм).
    """
    # Arrange (Подготовка)
    gram = range_model("грамм", 1)

    # Act (Действие)
    kg = range_model("кг", 1000, gram)

    # Assert (Проверка)
    assert kg.name == "кг"
    assert kg.conversion_factor == 1000
    assert kg.base_range is gram
    assert kg.base_range.name == "грамм"


def test_success_range_model_conversion_calculation():
    """
    Ожидание: Корректный пересчёт величин между единицами измерения (п. 10 ТЗ).
    Метод: range_model.conversion_factor
    Описание: Демонстрация работы с единицами: 2.5 кг пересчитываются в 2500 грамм
              через коэффициент пересчёта производной единицы.
    """
    # Arrange (Подготовка)
    gram = range_model("грамм", 1)
    kg = range_model("кг", 1000, gram)
    quantity_kg = 2.5

    # Act (Действие)
    quantity_gram = quantity_kg * kg.conversion_factor

    # Assert (Проверка)
    assert quantity_gram == 2500


def test_success_range_model_chain_conversion():
    """
    Ожидание: Корректный многоуровневый пересчёт (тонна -> кг -> грамм).
    Метод: range_model.conversion_factor
    Описание: Демонстрация цепочки пересчёта: 2 тонны = 2 * 1000 * 1000 = 2 000 000 грамм.
    """
    # Arrange (Подготовка)
    gram = range_model("грамм", 1)
    kg = range_model("кг", 1000, gram)
    ton = range_model("тонна", 1000, kg)

    # Act (Действие)
    quantity_gram = 2 * ton.conversion_factor * kg.conversion_factor

    # Assert (Проверка)
    assert quantity_gram == 2_000_000


def test_success_range_model_float_conversion_factor():
    """
    Ожидание: Успешное создание единицы с дробным коэффициентом пересчёта.
    Метод: range_model.__init__
    Описание: Миллиграмм с коэффициентом 0.001 относительно грамма корректно создаётся.
    """
    # Arrange & Act (Подготовка и Действие)
    gram = range_model("грамм", 1)
    mg = range_model("мг", 0.001, gram)

    # Assert (Проверка)
    assert mg.conversion_factor == 0.001
    assert mg.base_range is gram


def test_argument_exception_range_model_zero_factor():
    """
    Ожидание: Выброс argument_exception при нулевом коэффициенте пересчёта.
    Метод: range_model.conversion_factor (setter)
    Описание: Коэффициент пересчёта физически не может быть равен нулю.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        range_model("ошибка", 0)


def test_argument_exception_range_model_negative_factor():
    """
    Ожидание: Выброс argument_exception при отрицательном коэффициенте пересчёта.
    Метод: range_model.conversion_factor (setter)
    Описание: Коэффициент пересчёта физически не может быть отрицательным.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        range_model("ошибка", -5)


def test_argument_exception_range_model_string_factor():
    """
    Ожидание: Выброс argument_exception при передаче строки вместо числа.
    Метод: range_model.conversion_factor (setter)
    Описание: Коэффициент пересчёта должен быть числом (int или float), а не строкой.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        range_model("ошибка", "1000")


def test_argument_exception_range_model_invalid_base_type():
    """
    Ожидание: Выброс argument_exception при передаче строки в качестве базовой единицы.
    Метод: range_model.base_range (setter)
    Описание: Базовая единица измерения должна быть экземпляром range_model, а не строкой.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        range_model("кг", 1000, "грамм")


def test_success_range_model_create_kilogram():
    """
    Ожидание: Фабричный метод create_kilogram возвращает единицу 'килограмм' со значением 1000 и базой 'грамм'.
    Метод: range_model.create_kilogram
    Описание: Проверяет работу фабричного метода создания килограмма с дефолтными параметрами.
    """
    # Act
    kg = range_model.create_kilogram()

    # Assert
    assert kg.name == "килограмм"
    assert kg.value == 1000
    assert kg.base is not None
    assert kg.base.name == "грамм"


def test_success_range_model_create_kilogram_custom():
    """
    Ожидание: Фабричный метод create_kilogram с кастомными именами возвращает настроенный объект.
    Метод: range_model.create_kilogram
    Описание: Проверяет работу фабричного метода создания килограмма с переданными именами.
    """
    # Act
    kg = range_model.create_kilogram(name="Килограмм", base_name="Грамм")

    # Assert
    assert kg.name == "Килограмм"
    assert kg.value == 1000
    assert kg.base is not None
    assert kg.base.name == "Грамм"


def test_success_range_model_create_gram():
    """
    Ожидание: Фабричный метод create_gram возвращает единицу 'грамм' со значением 1 и базой None.
    Метод: range_model.create_gram
    Описание: Проверяет работу фабричного метода создания грамма.
    """
    # Act
    gram = range_model.create_gram()

    # Assert
    assert gram.name == "грамм"
    assert gram.value == 1
    assert gram.base is None


def test_success_range_model_create_liter_and_milliliter():
    """
    Ожидание: Фабричный метод create_liter возвращает единицу 'литр' со значением 1000 и базой 'миллилитр'.
    Метод: range_model.create_liter
    Описание: Проверяет работу фабричного метода создания литра и миллилитра.
    """
    # Act
    liter = range_model.create_liter()

    # Assert
    assert liter.name == "литр"
    assert liter.value == 1000
    assert liter.base is not None
    assert liter.base.name == "миллилитр"
    assert liter.base.value == 1


def test_success_range_model_create_piece():
    """
    Ожидание: Фабричный метод create_piece возвращает единицу 'штука' со значением 1 и базой None.
    Метод: range_model.create_piece
    Описание: Проверяет работу фабричного метода создания штуки.
    """
    # Act
    piece = range_model.create_piece()

    # Assert
    assert piece.name == "штука"
    assert piece.value == 1
    assert piece.base is None



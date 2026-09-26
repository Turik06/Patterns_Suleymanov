import pytest
from Src.Core.exception import argument_exception, max_length_exception
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model


def test_success_nomenclature_model_full_creation():
    """
    Ожидание: Успешное создание номенклатуры с полным набором параметров.
    Метод: nomenclature_model.__init__
    Описание: Номенклатура создаётся с кратким именем, полным именем, группой и единицей измерения.
    """
    # Arrange (Подготовка)
    gram = range_model("грамм", 1)
    group = nomenclature_group_model("Мясо")

    # Act (Действие)
    item = nomenclature_model("Говядина", "Говядина охлаждённая, вырезка", group, gram)

    # Assert (Проверка)
    assert item.name == "Говядина"
    assert item.full_name == "Говядина охлаждённая, вырезка"
    assert item.group is group
    assert item.range is gram


def test_success_nomenclature_model_boundary_255_full_name():
    """
    Ожидание: Успешное создание номенклатуры с полным именем ровно в 255 символов.
    Метод: nomenclature_model.full_name (setter)
    Описание: Граничное значение — полное наименование ровно в 255 символов допустимо.
    """
    # Arrange (Подготовка)
    gram = range_model("грамм", 1)
    group = nomenclature_group_model("Мясо")
    long_full_name = "А" * 255

    # Act (Действие)
    item = nomenclature_model("Говядина", long_full_name, group, gram)

    # Assert (Проверка)
    assert len(item.full_name) == 255


def test_argument_exception_nomenclature_model_full_name_too_long():
    """
    Ожидание: Выброс max_length_exception при полном наименовании длиннее 255 символов.
    Метод: nomenclature_model.full_name (setter)
    Описание: Полное наименование номенклатуры ограничено 255 символами (п. 7 ТЗ).
    """
    # Arrange (Подготовка)
    gram = range_model("грамм", 1)
    group = nomenclature_group_model("Мясо")
    too_long_name = "А" * 256

    # Act & Assert (Действие и Проверка)
    with pytest.raises(max_length_exception):
        nomenclature_model("Говядина", too_long_name, group, gram)


def test_argument_exception_nomenclature_model_empty_full_name():
    """
    Ожидание: Выброс argument_exception при пустом полном наименовании.
    Метод: nomenclature_model.full_name (setter)
    Описание: Полное наименование номенклатуры не может быть пустой строкой.
    """
    # Arrange (Подготовка)
    gram = range_model("грамм", 1)
    group = nomenclature_group_model("Мясо")

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        nomenclature_model("Говядина", "", group, gram)


def test_argument_exception_nomenclature_model_invalid_group_type():
    """
    Ожидание: Выброс argument_exception при передаче строки вместо объекта группы.
    Метод: nomenclature_model.group (setter)
    Описание: Поле group должно быть экземпляром nomenclature_group_model, а не строкой (п. 8 ТЗ).
    """
    # Arrange (Подготовка)
    gram = range_model("грамм", 1)

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        nomenclature_model("Говядина", "Говядина полное", "Мясо", gram)


def test_argument_exception_nomenclature_model_invalid_range_type():
    """
    Ожидание: Выброс argument_exception при передаче строки вместо объекта единицы измерения.
    Метод: nomenclature_model.range (setter)
    Описание: Поле range должно быть экземпляром range_model, а не строкой (п. 8 ТЗ).
    """
    # Arrange (Подготовка)
    group = nomenclature_group_model("Мясо")

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        nomenclature_model("Говядина", "Говядина полное", group, "грамм")

import pytest
from Src.Core.exception import max_length_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model


def test_success_nomenclature_group_model_creation():
    """
    Ожидание: Успешное создание группы номенклатуры.
    Метод: nomenclature_group_model.__init__
    Описание: Группа с валидным именем корректно создаётся и хранит наименование.
    """
    # Arrange & Act (Подготовка и Действие)
    group = nomenclature_group_model("Мясо")

    # Assert (Проверка)
    assert group.name == "Мясо"
    assert group.id is not None


def test_argument_exception_nomenclature_group_model_long_name():
    """
    Ожидание: Выброс max_length_exception при имени длиннее 50 символов.
    Метод: nomenclature_group_model.name (setter, наследован от name_id)
    Описание: Наименование группы ограничено 50 символами (п. 9 ТЗ).
    """
    # Arrange (Подготовка)
    long_name = "А" * 51

    # Act & Assert (Действие и Проверка)
    with pytest.raises(max_length_exception):
        nomenclature_group_model(long_name)


def test_success_nomenclature_group_model_boundary_50_chars():
    """
    Ожидание: Успешное создание группы с именем ровно в 50 символов.
    Метод: nomenclature_group_model.name (setter, наследован от name_id)
    Описание: Граничное значение — имя ровно в 50 символов допустимо.
    """
    # Arrange (Подготовка)
    exact_name = "А" * 50

    # Act (Действие)
    group = nomenclature_group_model(exact_name)

    # Assert (Проверка)
    assert len(group.name) == 50

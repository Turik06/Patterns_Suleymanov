import pytest
from Src.Core.exception import argument_exception
from Src.Models.storage_model import storage_model


def test_success_storage_model_creation():
    """
    Ожидание: Успешное создание склада.
    Метод: storage_model.__init__
    Описание: Склад с валидным именем корректно создаётся.
    """
    # Arrange & Act (Подготовка и Действие)
    storage = storage_model("Основной склад")

    # Assert (Проверка)
    assert storage.name == "Основной склад"
    assert storage.id is not None
    assert storage.address == ""


def test_success_storage_model_creation_with_address():
    """
    Ожидание: Успешное создание склада с указанием адреса.
    Метод: storage_model.__init__
    Описание: Склад с наименованием и адресом корректно сохраняет оба параметра.
    """
    # Arrange & Act (Подготовка и Действие)
    storage = storage_model("Основной склад", "г. Москва, ул. Мира, д. 10")

    # Assert (Проверка)
    assert storage.name == "Основной склад"
    assert storage.address == "г. Москва, ул. Мира, д. 10"


def test_argument_exception_storage_model_invalid_address_type():
    """
    Ожидание: Выброс argument_exception при передаче нестрокового адреса.
    Метод: storage_model.address (setter)
    Описание: Адрес склада должен быть строкой.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        storage_model("Основной склад", 12345)


def test_argument_exception_storage_model_empty_name():
    """
    Ожидание: Выброс argument_exception при пустом имени склада.
    Метод: storage_model.name (setter, наследован от name_id)
    Описание: Имя склада не может быть пустой строкой.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        storage_model("")


def test_argument_exception_storage_model_whitespace_name():
    """
    Ожидание: Выброс argument_exception при имени из одних пробелов.
    Метод: storage_model.name (setter, наследован от name_id)
    Описание: Строка только из пробелов обрезается (strip) и считается пустой.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        storage_model("   ")


def test_false_eq_storage_model_compare_with_string():
    """
    Ожидание: Сравнение модели со строкой возвращает False без ошибки.
    Метод: name_id.__eq__
    Описание: Оператор == не должен падать при сравнении сущности с объектом другого типа.
    """
    # Arrange (Подготовка)
    storage = storage_model("Основной склад")

    # Act & Assert (Действие и Проверка)
    assert storage != "Основной склад"
    assert storage != 123


def test_false_eq_storage_model_same_name_different_id():
    """
    Ожидание: Два склада с одинаковым именем, но разными ID — не равны.
    Метод: name_id.__eq__
    Описание: Сущности сравниваются по id, а не по значению name.
    """
    # Arrange (Подготовка)
    storage1 = storage_model("Основной склад")
    storage2 = storage_model("Основной склад")

    # Act & Assert (Действие и Проверка)
    assert storage1 != storage2
    assert storage1.name == storage2.name

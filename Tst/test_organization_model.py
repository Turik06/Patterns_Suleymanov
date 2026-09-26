import pytest
from Src.Core.exception import argument_exception
from Src.Models.organization_model import organization_model


def test_success_organization_model_inn_10_digits():
    """
    Ожидание: Успешное создание организации с 10-значным ИНН (юридическое лицо).
    Метод: organization_model.__init__
    Описание: ООО Ромашка с корректным набором реквизитов создаётся без ошибок.
    """
    # Arrange & Act (Подготовка и Действие)
    org = organization_model("Ромашка", "1234567890", "044525225", "40702810938000012345", "ООО")

    # Assert (Проверка)
    assert org.name == "Ромашка"
    assert org.inn == "1234567890"
    assert org.bik == "044525225"
    assert org.account == "40702810938000012345"
    assert org.ownership_form == "ООО"


def test_success_organization_model_inn_12_digits():
    """
    Ожидание: Успешное создание организации с 12-значным ИНН (индивидуальный предприниматель).
    Метод: organization_model.__init__
    Описание: ИП с 12-значным ИНН создаётся без ошибок.
    """
    # Arrange & Act (Подготовка и Действие)
    org = organization_model("Иванов", "123456789012", "044525225", "40802810938000012345", "ИП")

    # Assert (Проверка)
    assert org.inn == "123456789012"
    assert org.ownership_form == "ИП"


def test_argument_exception_organization_model_invalid_inn_length():
    """
    Ожидание: Выброс argument_exception при некорректной длине ИНН (не 10 и не 12).
    Метод: organization_model.inn (setter)
    Описание: ИНН длиной 8 цифр не соответствует стандарту РФ.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        organization_model("Ромашка", "12345678", "044525225", "40702810938000012345", "ООО")


def test_argument_exception_organization_model_inn_with_letters():
    """
    Ожидание: Выброс argument_exception при наличии букв в ИНН.
    Метод: organization_model.inn (setter)
    Описание: ИНН должен содержать только цифры, буквы недопустимы.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        organization_model("Ромашка", "123456789A", "044525225", "40702810938000012345", "ООО")


def test_argument_exception_organization_model_inn_as_int():
    """
    Ожидание: Выброс argument_exception при передаче ИНН как числа int.
    Метод: organization_model.inn (setter)
    Описание: ИНН должен быть строкой, а не числом (ведущие нули теряются в числовом типе).
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        organization_model("Ромашка", 1234567890, "044525225", "40702810938000012345", "ООО")


def test_argument_exception_organization_model_invalid_bik():
    """
    Ожидание: Выброс argument_exception при некорректной длине БИК.
    Метод: organization_model.bik (setter)
    Описание: БИК должен содержать ровно 9 цифр, 7 цифр — это ошибка.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "1234567", "40702810938000012345", "ООО")


def test_argument_exception_organization_model_invalid_account():
    """
    Ожидание: Выброс argument_exception при некорректной длине счёта.
    Метод: organization_model.account (setter)
    Описание: Расчётный счёт должен содержать ровно 20 цифр.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "044525225", "12345", "ООО")


def test_argument_exception_organization_model_long_ownership_form():
    """
    Ожидание: Выброс argument_exception при форме собственности длиннее 5 символов.
    Метод: organization_model.ownership_form (setter)
    Описание: Форма собственности — краткая аббревиатура, максимум 5 символов.
    """
    # Arrange, Act & Assert (Подготовка, Действие и Проверка)
    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "044525225", "40702810938000012345", "ДЛИННАЯ")


def test_argument_exception_organization_model_setter_invalid_bik():
    """
    Ожидание: Выброс argument_exception при изменении БИК на невалидный через сеттер.
    Метод: organization_model.bik (setter)
    Описание: Валидация срабатывает не только при создании, но и при последующем изменении поля.
    """
    # Arrange (Подготовка)
    org = organization_model("Ромашка", "1234567890", "044525225", "40702810938000012345", "ООО")

    # Act & Assert (Действие и Проверка)
    with pytest.raises(argument_exception):
        org.bik = "123"

import pytest
from Src.Core.common import common
from Src.Core.exception import argument_exception
from Src.Models.range_model import range_model


def test_error_common_get_fields_none():
    """
    Ожидание: Исключение argument_exception при передаче None в source.
    Метод: common.get_fields
    Описание: При передаче None в качестве источника метод должен выбрасывать argument_exception.
    """
    # Arrange, Act & Assert
    with pytest.raises(argument_exception):
        common.get_fields(None)


def test_success_common_get_fields_model():
    """
    Ожидание: Возврат списка публичных свойств модели.
    Метод: common.get_fields
    Описание: Метод возвращает имена всех свойств (property) переданного объекта.
    """
    # Arrange
    item = range_model("грамм", 1)

    # Act
    fields = common.get_fields(item)

    # Assert
    assert isinstance(fields, list)
    assert "name" in fields
    assert "id" in fields
    assert "conversion_factor" in fields


def test_success_common_get_fields_is_common_filter():
    """
    Ожидание: Фильтрация списков и словарей при флаге is_common=True.
    Метод: common.get_fields
    Описание: Если флаг is_common=True, свойства, возвращающие list или dict, исключаются из результата.
    """
    # Arrange
    class dummy_model:
        """Вспомогательная модель для проверки фильтрации свойств."""

        @property
        def text(self):
            """Простое строковое свойство."""
            return "sample"

        @property
        def items(self):
            """Свойство, возвращающее список."""
            return [1, 2, 3]

        @property
        def mapping(self):
            """Свойство, возвращающее словарь."""
            return {"key": "value"}

    obj = dummy_model()

    # Act
    all_fields = common.get_fields(obj, is_common=False)
    simple_fields = common.get_fields(obj, is_common=True)

    # Assert
    assert set(all_fields) == {"text", "items", "mapping"}
    assert simple_fields == ["text"]

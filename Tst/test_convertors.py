import pytest
from datetime import date, datetime
from Src.Core.abstract_convertor import abstract_convertor, abstract_covertor
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


class TestAbstractConvertor:
    """Тесты абстрактного контракта abstract_convertor."""

    def test_abstract_cannot_be_instantiated(self):
        """Проверка невозможности создания экземпляра абстрактного класса."""
        with pytest.raises(TypeError):
            abstract_convertor()

    def test_abstract_covertor_alias(self):
        """Проверка наличия алиаса abstract_covertor для совместимости с ТЗ."""
        assert abstract_covertor is abstract_convertor

    def test_convert_alias_with_capital_letter(self):
        """Проверка работы алиаса Convert с заглавной буквы."""
        conv = basic_convertor()
        result = conv.Convert("field", 123)
        assert result == {"field": 123}


class TestBasicConvertor:
    """Тесты базового конвертера простых типов basic_convertor."""

    def test_convert_integer(self):
        conv = basic_convertor()
        assert conv.convert("count", 10) == {"count": 10}

    def test_convert_float(self):
        conv = basic_convertor()
        assert conv.convert("price", 19.99) == {"price": 19.99}

    def test_convert_string(self):
        conv = basic_convertor()
        assert conv.convert("name", "Тестовая строка") == {"name": "Тестовая строка"}

    def test_convert_bool(self):
        conv = basic_convertor()
        assert conv.convert("is_active", True) == {"is_active": True}
        assert conv.convert("is_deleted", False) == {"is_deleted": False}

    def test_convert_none(self):
        conv = basic_convertor()
        assert conv.convert("nullable_field", None) == {"nullable_field": None}

    def test_convert_invalid_field_raises(self):
        conv = basic_convertor()
        with pytest.raises(argument_exception):
            conv.convert("", 10)

        with pytest.raises(argument_exception):
            conv.convert("   ", 10)

        with pytest.raises(argument_exception):
            conv.convert(None, 10)

        with pytest.raises(argument_exception):
            conv.convert(123, 10)

    def test_convert_invalid_type_raises(self):
        conv = basic_convertor()
        with pytest.raises(argument_exception):
            conv.convert("field", [1, 2, 3])

        with pytest.raises(argument_exception):
            conv.convert("field", {"k": "v"})


class TestDatetimeConvertor:
    """Тесты конвертера даты и времени datetime_convertor."""

    def test_convert_datetime(self):
        conv = datetime_convertor()
        dt = datetime(2026, 10, 21, 15, 30, 45)
        assert conv.convert("created_at", dt) == {"created_at": "2026-10-21T15:30:45"}

    def test_convert_date(self):
        conv = datetime_convertor()
        d = date(2026, 10, 21)
        assert conv.convert("birth_date", d) == {"birth_date": "2026-10-21"}

    def test_convert_invalid_field_raises(self):
        conv = datetime_convertor()
        dt = datetime(2026, 1, 1)
        with pytest.raises(argument_exception):
            conv.convert("", dt)

        with pytest.raises(argument_exception):
            conv.convert(None, dt)

    def test_convert_invalid_type_raises(self):
        conv = datetime_convertor()
        with pytest.raises(argument_exception):
            conv.convert("date", "2026-10-21")

        with pytest.raises(argument_exception):
            conv.convert("date", 12345678)

        with pytest.raises(argument_exception):
            conv.convert("date", None)


class TestReferenceConvertor:
    """Тесты конвертера ссылочных доменных моделей reference_convertor."""

    def test_convert_group_model(self):
        conv = reference_convertor()
        group = nomenclature_group_model("Сырье")
        res = conv.convert("group", group)
        assert "group" in res
        assert res["group"]["id"] == group.id
        assert res["group"]["name"] == "Сырье"

    def test_convert_without_field_name(self):
        conv = reference_convertor()
        group = nomenclature_group_model("Сырье")
        res = conv.convert("", group)
        assert res["id"] == group.id
        assert res["name"] == "Сырье"

    def test_convert_nested_range_model(self):
        conv = reference_convertor()
        gram = range_model("грамм", 1, None)
        kg = range_model("кг", 1000, gram)

        res = conv.convert("unit", kg)
        unit_data = res["unit"]
        assert unit_data["id"] == kg.id
        assert unit_data["name"] == "кг"
        assert unit_data["conversion_factor"] == 1000
        assert unit_data["base_range"] is not None
        assert unit_data["base_range"]["id"] == gram.id
        assert unit_data["base_range"]["name"] == "грамм"
        assert unit_data["base_range"]["base_range"] is None

    def test_convert_nomenclature_model(self):
        conv = reference_convertor()
        group = nomenclature_group_model("Молочные")
        unit = range_model("литр", 1, None)
        item = nomenclature_model("Молоко", "Молоко пастеризованное 3.2%", group, unit)

        res = conv.convert("item", item)
        data = res["item"]
        assert data["id"] == item.id
        assert data["name"] == "Молоко"
        assert data["full_name"] == "Молоко пастеризованное 3.2%"
        assert data["group"]["name"] == "Молочные"
        assert data["range"]["name"] == "литр"

    def test_convert_storage_model(self):
        conv = reference_convertor()
        storage = storage_model("Основной склад", "ул. Ленина, 1")
        res = conv.convert("storage", storage)
        assert res["storage"]["name"] == "Основной склад"
        assert res["storage"]["address"] == "ул. Ленина, 1"

    def test_circular_reference_protection(self):
        conv = reference_convertor()
        r1 = range_model("r1")
        r2 = range_model("r2")
        r1.base_range = r2
        r2.base_range = r1

        res = conv.convert("r1", r1)
        assert res["r1"]["name"] == "r1"
        assert res["r1"]["base_range"]["name"] == "r2"
        # Циклическая ссылка должна разрешиться в краткий словарь без бесконечной рекурсии
        assert res["r1"]["base_range"]["base_range"]["id"] == r1.id
        assert res["r1"]["base_range"]["base_range"]["name"] == "r1"

    def test_invalid_obj_type_raises(self):
        conv = reference_convertor()
        with pytest.raises(argument_exception):
            conv.convert("model", "not a model")

        with pytest.raises(argument_exception):
            conv.convert("model", 123)

        with pytest.raises(argument_exception):
            conv.convert("model", None)

    def test_single_argument_calls(self):
        """Проверка вызова конвертеров с одним аргументом (непосредственно передача объекта)."""
        b_conv = basic_convertor()
        assert b_conv.convert(100) == {"value": 100}
        assert b_conv.Convert("abc") == {"value": "abc"}

        dt_conv = datetime_convertor()
        d = date(2026, 10, 21)
        assert dt_conv.convert(d) == {"value": "2026-10-21"}

        r_conv = reference_convertor()
        group = nomenclature_group_model("Группа тестовая")
        res = r_conv.convert(group)
        assert res["name"] == "Группа тестовая"
        assert "id" in res

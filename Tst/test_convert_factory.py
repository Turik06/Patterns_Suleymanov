import io
import json
import pytest
from datetime import date, datetime
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.storage_model import storage_model


class TestConvertFactory:
    """Тесты фабрики конвертации и сериализации convert_factory."""

    def test_factory_resolves_default_convertors(self):
        factory = convert_factory()

        assert isinstance(factory.get_convertor(10), basic_convertor)
        assert isinstance(factory.get_convertor(10.5), basic_convertor)
        assert isinstance(factory.get_convertor("строка"), basic_convertor)
        assert isinstance(factory.get_convertor(True), basic_convertor)
        assert isinstance(factory.get_convertor(None), basic_convertor)

        assert isinstance(factory.get_convertor(datetime.now()), datetime_convertor)
        assert isinstance(factory.get_convertor(date.today()), datetime_convertor)

        group = nomenclature_group_model("Группа")
        assert isinstance(factory.get_convertor(group), reference_convertor)

    def test_factory_create_alias(self):
        factory = convert_factory()
        assert isinstance(factory.create(123), basic_convertor)

    def test_factory_register_custom_type(self):
        factory = convert_factory()

        class custom_class:
            pass

        class custom_convertor(abstract_convertor):
            def convert(self, field: str, obj):
                return {field: "custom_ok"}

        factory.register(custom_class, custom_convertor)
        conv = factory.get_convertor(custom_class())
        assert isinstance(conv, custom_convertor)
        assert factory.convert("result", custom_class()) == {"result": "custom_ok"}

    def test_factory_register_invalid_arguments_raises(self):
        factory = convert_factory()
        with pytest.raises(argument_exception):
            factory.register("not_a_type", basic_convertor)

        with pytest.raises(argument_exception):
            factory.register(int, "not_a_convertor_class")

    def test_factory_get_convertor_unregistered_raises(self):
        factory = convert_factory()

        class unk:
            pass

        with pytest.raises(argument_exception):
            factory.get_convertor(unk())

    def test_factory_convert_primitives(self):
        factory = convert_factory()
        assert factory.convert("val", 42) == {"val": 42}
        assert factory.convert("val", 3.14) == {"val": 3.14}
        assert factory.convert("val", "hello") == {"val": "hello"}
        assert factory.convert("val", False) == {"val": False}
        assert factory.convert("val", None) == {"val": None}

    def test_factory_convert_list(self):
        factory = convert_factory()
        group1 = nomenclature_group_model("Группа 1")
        group2 = nomenclature_group_model("Группа 2")

        res = factory.convert("groups", [group1, group2])
        assert "groups" in res
        assert len(res["groups"]) == 2
        assert res["groups"][0]["name"] == "Группа 1"
        assert res["groups"][1]["name"] == "Группа 2"

    def test_deep_recursion_range_chain(self):
        """Проверка рекурсивной цепочки единиц измерения: тонна -> кг -> грамм (схема с доски)."""
        factory = convert_factory()

        gram = range_model("грамм", 1, None)
        kg = range_model("кг", 1000, gram)
        ton = range_model("тонна", 1000, kg)

        json_text = factory.to_json(ton)
        data = json.loads(json_text)

        assert data["name"] == "тонна"
        assert data["conversion_factor"] == 1000
        assert data["base_range"]["name"] == "кг"
        assert data["base_range"]["conversion_factor"] == 1000
        assert data["base_range"]["base_range"]["name"] == "грамм"
        assert data["base_range"]["base_range"]["conversion_factor"] == 1
        assert data["base_range"]["base_range"]["base_range"] is None

    def test_deep_recursion_recipe_with_subrecipe(self):
        """Проверка рекурсии рецепта с вложенным полуфабрикатом (sub_recipe)."""
        factory = convert_factory()

        g = nomenclature_group_model("Ингредиенты")
        unit_g = range_model("грамм", 1, None)
        flour = nomenclature_model("Мука", "Мука в/с", g, unit_g)
        sugar = nomenclature_model("Сахар", "Сахар белый", g, unit_g)

        # Полуфабрикат: Тесто
        dough_recipe = recipe_model("Тесто песочное")
        dough_row = recipe_row_model.create_ingredient(flour, 200, 200)
        dough_recipe.add_row(dough_row)

        # Основной рецепт: Печенье, включающий тесто как подрецепт
        cookie_recipe = recipe_model("Печенье к чаю")
        cookie_row1 = recipe_row_model(
            nomenclature=nomenclature_model("Тесто", "Тесто заготовка", g, unit_g),
            sub_recipe=dough_recipe,
        )
        cookie_row2 = recipe_row_model.create_ingredient(sugar, 50, 50)
        cookie_recipe.add_row(cookie_row1)
        cookie_recipe.add_row(cookie_row2)

        json_text = factory.to_json(cookie_recipe)
        data = json.loads(json_text)

        assert data["name"] == "Печенье к чаю"
        assert len(data["rows"]) == 2
        # Строка 1 содержит вложенный рецепт теста
        assert data["rows"][0]["sub_recipe"] is not None
        assert data["rows"][0]["sub_recipe"]["name"] == "Тесто песочное"
        assert len(data["rows"][0]["sub_recipe"]["rows"]) == 1
        assert data["rows"][0]["sub_recipe"]["rows"][0]["name"] == "Мука"

    def test_serialize_storage_manager_data(self):
        """Проверка сериализации полных данных storage_manager.data."""
        sm = storage_manager()
        sm.load()
        factory = convert_factory()

        json_text = factory.to_json(sm.data)
        assert isinstance(json_text, str)
        assert len(json_text) > 0

        # Проверка обратной загрузки
        data = json.loads(json_text)
        assert "storage_model" in data
        assert "range_model" in data
        assert "group_model" in data
        assert "nomenclature_model" in data
        assert "receipt_model" in data

    def test_factory_dump_to_file_stream(self):
        """Проверка выгрузки JSON в файловый поток через dump."""
        factory = convert_factory()
        group = nomenclature_group_model("Тест стрима")

        stream = io.StringIO()
        factory.dump(group, stream)
        stream.seek(0)
        loaded = json.loads(stream.read())
        assert loaded["name"] == "Тест стрима"

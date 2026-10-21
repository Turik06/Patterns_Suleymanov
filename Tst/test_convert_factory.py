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
    """
    Набор модульных тестов для фабрики конвертации и сериализации convert_factory
    """

    def test_success_convert_factory_resolves_default_convertors(self):
        """
        Ожидание: Автоматическое определение конвертера по типу переданного объекта.
        Метод: convert_factory.get_convertor
        Описание: Проверяет подбор basic_convertor, datetime_convertor и reference_convertor для стандартных типов.
        """
        # Arrange (Подготовка)
        factory = convert_factory()
        group = nomenclature_group_model("Группа")

        # Act & Assert (Действие и Проверка)
        assert isinstance(factory.get_convertor(10), basic_convertor)
        assert isinstance(factory.get_convertor(10.5), basic_convertor)
        assert isinstance(factory.get_convertor("строка"), basic_convertor)
        assert isinstance(factory.get_convertor(True), basic_convertor)
        assert isinstance(factory.get_convertor(None), basic_convertor)

        assert isinstance(factory.get_convertor(datetime.now()), datetime_convertor)
        assert isinstance(factory.get_convertor(date.today()), datetime_convertor)
        assert isinstance(factory.get_convertor(group), reference_convertor)

    def test_success_convert_factory_create_alias(self):
        """
        Ожидание: Метод create работает идентично get_convertor.
        Метод: convert_factory.create
        Описание: Проверяет соответствие каноническому интерфейсу шаблона Factory.
        """
        # Arrange (Подготовка)
        factory = convert_factory()

        # Act & Assert (Действие и Проверка)
        assert isinstance(factory.create(123), basic_convertor)

    def test_success_convert_factory_register_custom_type(self):
        """
        Ожидание: Успешная регистрация и использование пользовательского конвертера.
        Метод: convert_factory.register
        Описание: Проверяет принцип открытости/закрытости (OCP) при добавлении нового типа.
        """
        # Arrange (Подготовка)
        factory = convert_factory()

        class custom_class:
            pass

        class custom_convertor(abstract_convertor):
            def convert(self, field: str, obj):
                return {field: "custom_ok"}

        # Act (Действие)
        factory.register(custom_class, custom_convertor)
        conv = factory.get_convertor(custom_class())
        result = factory.convert("result", custom_class())

        # Assert (Проверка)
        assert isinstance(conv, custom_convertor)
        assert result == {"result": "custom_ok"}

    def test_fail_convert_factory_register_invalid_arguments_raises(self):
        """
        Ожидание: Исключение argument_exception при невалидных типах в методе register.
        Метод: convert_factory.register
        Описание: Проверяет валидацию параметров target_type и convertor_cls.
        """
        # Arrange (Подготовка)
        factory = convert_factory()

        # Act & Assert (Действие и Проверка)
        with pytest.raises(argument_exception):
            factory.register("not_a_type", basic_convertor)

        with pytest.raises(argument_exception):
            factory.register(int, "not_a_convertor_class")

    def test_fail_convert_factory_get_convertor_unregistered_raises(self):
        """
        Ожидание: Исключение argument_exception при запросе конвертера для неизвестного типа.
        Метод: convert_factory.get_convertor
        Описание: Проверяет поведение при отсутствии зарегистрированного конвертера.
        """
        # Arrange (Подготовка)
        factory = convert_factory()

        class unk:
            pass

        # Act & Assert (Действие и Проверка)
        with pytest.raises(argument_exception):
            factory.get_convertor(unk())

    def test_success_convert_factory_convert_primitives(self):
        """
        Ожидание: Корректное делегирование сериализации примитивных типов базовому конвертеру.
        Метод: convert_factory.convert
        Описание: Проверяет числа, строки, булевы значения и None через фасад фабрики.
        """
        # Arrange (Подготовка)
        factory = convert_factory()

        # Act & Assert (Действие и Проверка)
        assert factory.convert("val", 42) == {"val": 42}
        assert factory.convert("val", 3.14) == {"val": 3.14}
        assert factory.convert("val", "hello") == {"val": "hello"}
        assert factory.convert("val", False) == {"val": False}
        assert factory.convert("val", None) == {"val": None}

    def test_success_convert_factory_convert_list(self):
        """
        Ожидание: Сериализация списка доменных моделей во вложенный список словарей.
        Метод: convert_factory.convert
        Описание: Проверяет обработку списков и итерируемых коллекций.
        """
        # Arrange (Подготовка)
        factory = convert_factory()
        group1 = nomenclature_group_model("Группа 1")
        group2 = nomenclature_group_model("Группа 2")

        # Act (Действие)
        res = factory.convert("groups", [group1, group2])

        # Assert (Проверка)
        assert "groups" in res
        assert len(res["groups"]) == 2
        assert res["groups"][0]["name"] == "Группа 1"
        assert res["groups"][1]["name"] == "Группа 2"

    def test_success_convert_factory_deep_recursion_range_chain(self):
        """
        Ожидание: Корректная сериализация многоуровневой цепочки единиц измерения: тонна -> кг -> грамм.
        Метод: convert_factory.to_json
        Описание: Проверяет рекурсивный спуск по свойству base_range до базовой единицы.
        """
        # Arrange (Подготовка)
        factory = convert_factory()
        gram = range_model("грамм", 1, None)
        kg = range_model("кг", 1000, gram)
        ton = range_model("тонна", 1000, kg)

        # Act (Действие)
        json_text = factory.to_json(ton)
        data = json.loads(json_text)

        # Assert (Проверка)
        assert data["name"] == "тонна"
        assert data["conversion_factor"] == 1000
        assert data["base_range"]["name"] == "кг"
        assert data["base_range"]["conversion_factor"] == 1000
        assert data["base_range"]["base_range"]["name"] == "грамм"
        assert data["base_range"]["base_range"]["conversion_factor"] == 1
        assert data["base_range"]["base_range"]["base_range"] is None

    def test_success_convert_factory_deep_recursion_recipe_with_subrecipe(self):
        """
        Ожидание: Корректная сериализация технологической карты с вложенным полуфабрикатом sub_recipe.
        Метод: convert_factory.to_json
        Описание: Проверяет рекурсивное разворачивание составного рецепта и его ингредиентов.
        """
        # Arrange (Подготовка)
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

        # Act (Действие)
        json_text = factory.to_json(cookie_recipe)
        data = json.loads(json_text)

        # Assert (Проверка)
        assert data["name"] == "Печенье к чаю"
        assert len(data["rows"]) == 2
        assert data["rows"][0]["sub_recipe"] is not None
        assert data["rows"][0]["sub_recipe"]["name"] == "Тесто песочное"
        assert len(data["rows"][0]["sub_recipe"]["rows"]) == 1
        assert data["rows"][0]["sub_recipe"]["rows"][0]["name"] == "Мука"

    def test_success_convert_factory_serialize_storage_manager_data(self):
        """
        Ожидание: Сериализация полного словаря данных хранилища storage_manager.data.
        Метод: convert_factory.to_json
        Описание: Проверяет экспорт всех категорий склада (склады, единицы, группы, номенклатура, рецепты).
        """
        # Arrange (Подготовка)
        sm = storage_manager()
        sm.load()
        factory = convert_factory()

        # Act (Действие)
        json_text = factory.to_json(sm.data)

        # Assert (Проверка)
        assert isinstance(json_text, str)
        assert len(json_text) > 0
        data = json.loads(json_text)
        assert "storage_model" in data
        assert "range_model" in data
        assert "group_model" in data
        assert "nomenclature_model" in data
        assert "receipt_model" in data

    def test_success_convert_factory_dump_to_file_stream(self):
        """
        Ожидание: Корректная выгрузка сериализованного JSON в файловый поток.
        Метод: convert_factory.dump
        Описание: Проверяет метод dump с объектом StringIO.
        """
        # Arrange (Подготовка)
        factory = convert_factory()
        group = nomenclature_group_model("Тест стрима")
        stream = io.StringIO()

        # Act (Действие)
        factory.dump(group, stream)
        stream.seek(0)
        loaded = json.loads(stream.read())

        # Assert (Проверка)
        assert loaded["name"] == "Тест стрима"

    def test_success_convert_factory_convert_single_argument(self):
        """
        Ожидание: Корректная работа convert и Convert при передаче только одного объекта.
        Метод: convert_factory.convert
        Описание: Проверяет вызов методов фабрики без указания внешнего ключа поля.
        """
        # Arrange (Подготовка)
        factory = convert_factory()
        group = nomenclature_group_model("Тест одного аргумента")

        # Act (Действие)
        res1 = factory.convert(group)
        res2 = factory.Convert(group)

        # Assert (Проверка)
        assert isinstance(res1, dict)
        assert res1["name"] == "Тест одного аргумента"
        assert res2["name"] == "Тест одного аргумента"

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
    """
    Набор модульных тестов для абстрактного класса abstract_convertor
    """

    def test_fail_abstract_convertor_instantiation_raises_type_error(self):
        """
        Ожидание: Исключение TypeError при попытке прямого инстанциирования абстрактного класса.
        Метод: abstract_convertor.__init__
        Описание: Проверяет невозможность создания объекта абстрактного класса ABC.
        """
        # Arrange & Act & Assert (Подготовка, Действие и Проверка)
        with pytest.raises(TypeError):
            abstract_convertor()

    def test_success_abstract_convertor_alias_covertor(self):
        """
        Ожидание: Наличие алиаса abstract_covertor, ссылающегося на abstract_convertor.
        Метод: abstract_convertor (alias)
        Описание: Проверяет обратную совместимость с возможной опечаткой в техническом задании.
        """
        # Arrange & Act & Assert
        assert abstract_covertor is abstract_convertor


class TestBasicConvertor:
    """
    Набор модульных тестов для конвертера простых типов basic_convertor
    """

    def test_success_basic_convertor_convert_integer(self):
        """
        Ожидание: Корректное преобразование целочисленного значения в словарь.
        Метод: basic_convertor.convert
        Описание: Проверяет формирование словаря вида {'count': 10}.
        """
        # Arrange (Подготовка)
        conv = basic_convertor()

        # Act (Действие)
        result = conv.convert("count", 10)

        # Assert (Проверка)
        assert result == {"count": 10}

    def test_success_basic_convertor_convert_float(self):
        """
        Ожидание: Корректное преобразование числа с плавающей точкой в словарь.
        Метод: basic_convertor.convert
        Описание: Проверяет сохранение точности вещественного числа.
        """
        # Arrange (Подготовка)
        conv = basic_convertor()

        # Act (Действие)
        result = conv.convert("price", 19.99)

        # Assert (Проверка)
        assert result == {"price": 19.99}

    def test_success_basic_convertor_convert_string(self):
        """
        Ожидание: Корректное преобразование строки в словарь.
        Метод: basic_convertor.convert
        Описание: Проверяет строковое значение в словаре.
        """
        # Arrange (Подготовка)
        conv = basic_convertor()

        # Act (Действие)
        result = conv.convert("name", "Тестовая строка")

        # Assert (Проверка)
        assert result == {"name": "Тестовая строка"}

    def test_success_basic_convertor_convert_boolean(self):
        """
        Ожидание: Корректное преобразование логических значений True и False.
        Метод: basic_convertor.convert
        Описание: Проверяет булевы флаги в результирующем словаре.
        """
        # Arrange (Подготовка)
        conv = basic_convertor()

        # Act & Assert (Действие и Проверка)
        assert conv.convert("is_active", True) == {"is_active": True}
        assert conv.convert("is_deleted", False) == {"is_deleted": False}

    def test_success_basic_convertor_convert_none(self):
        """
        Ожидание: Корректное сохранение значения None в словаре.
        Метод: basic_convertor.convert
        Описание: Проверяет поддержку пустых (nullable) значений.
        """
        # Arrange (Подготовка)
        conv = basic_convertor()

        # Act (Действие)
        result = conv.convert("nullable_field", None)

        # Assert (Проверка)
        assert result == {"nullable_field": None}

    def test_fail_basic_convertor_convert_invalid_field_raises(self):
        """
        Ожидание: Исключение argument_exception при некорректном имени поля.
        Метод: basic_convertor.convert
        Описание: Проверяет валидацию пустых строк, пробелов, None и нестроковых ключей.
        """
        # Arrange (Подготовка)
        conv = basic_convertor()

        # Act & Assert (Действие и Проверка)
        with pytest.raises(argument_exception):
            conv.convert("", 10)

        with pytest.raises(argument_exception):
            conv.convert("   ", 10)

        with pytest.raises(argument_exception):
            conv.convert(None, 10)

        with pytest.raises(argument_exception):
            conv.convert(123, 10)

    def test_fail_basic_convertor_convert_invalid_type_raises(self):
        """
        Ожидание: Исключение argument_exception при передаче неподдерживаемых составных типов.
        Метод: basic_convertor.convert
        Описание: Проверяет отсечение списков и словарей базовым конвертером.
        """
        # Arrange (Подготовка)
        conv = basic_convertor()

        # Act & Assert (Действие и Проверка)
        with pytest.raises(argument_exception):
            conv.convert("field", [1, 2, 3])

        with pytest.raises(argument_exception):
            conv.convert("field", {"k": "v"})

    def test_success_basic_convertor_convert_model_numbers_and_strings(self):
        """
        Ожидание: Извлечение словаря числовых и строковых свойств модели при вызове с одним аргументом.
        Метод: basic_convertor.convert
        Описание: Проверяет извлечение примитивных свойств (name, conversion_factor, id) из range_model и пропуск ссылок.
        """
        # Arrange (Подготовка)
        conv = basic_convertor()
        kg = range_model("килограмм", 1000, None)

        # Act (Действие)
        res = conv.convert(kg)

        # Assert (Проверка)
        assert isinstance(res, dict)
        assert res["name"] == "килограмм"
        assert res["conversion_factor"] == 1000
        assert res["id"] == str(kg.id)
        assert "base_range" not in res

    def test_success_basic_convertor_convert_composite_skips_non_primitives(self):
        """
        Ожидание: Пропуск ссылок на другие сущности при извлечении примитивных свойств модели.
        Метод: basic_convertor.convert
        Описание: Проверяет, что у nomenclature_model извлекаются id, name, full_name, а group и range пропускаются.
        """
        # Arrange (Подготовка)
        conv = basic_convertor()
        group = nomenclature_group_model("Бакалея")
        unit = range_model("килограмм", 1000, None)
        item = nomenclature_model("Мука", "Мука пшеничная", group, unit)

        # Act (Действие)
        res = conv.convert(item)

        # Assert (Проверка)
        assert res["name"] == "Мука"
        assert res["full_name"] == "Мука пшеничная"
        assert res["id"] == str(item.id)
        assert "group" not in res
        assert "range" not in res


class TestDatetimeConvertor:
    """
    Набор модульных тестов для конвертера даты и времени datetime_convertor
    """

    def test_success_datetime_convertor_convert_datetime(self):
        """
        Ожидание: Преобразование объекта datetime в строковый формат ISO 8601.
        Метод: datetime_convertor.convert
        Описание: Проверяет формат вывода даты и времени вида YYYY-MM-DDTHH:MM:SS.
        """
        # Arrange (Подготовка)
        conv = datetime_convertor()
        dt = datetime(2026, 10, 21, 15, 30, 45)

        # Act (Действие)
        result = conv.convert("created_at", dt)

        # Assert (Проверка)
        assert result == {"created_at": "2026-10-21T15:30:45"}

    def test_success_datetime_convertor_convert_date(self):
        """
        Ожидание: Преобразование объекта date в формат ISO 8601 YYYY-MM-DD.
        Метод: datetime_convertor.convert
        Описание: Проверяет корректность работы с чистым типом date.
        """
        # Arrange (Подготовка)
        conv = datetime_convertor()
        d = date(2026, 10, 21)

        # Act (Действие)
        result = conv.convert("birth_date", d)

        # Assert (Проверка)
        assert result == {"birth_date": "2026-10-21"}

    def test_fail_datetime_convertor_convert_invalid_field_raises(self):
        """
        Ожидание: Исключение argument_exception при пустом или нестроковом наименовании поля.
        Метод: datetime_convertor.convert
        Описание: Проверяет валидацию параметра field.
        """
        # Arrange (Подготовка)
        conv = datetime_convertor()
        dt = datetime(2026, 1, 1)

        # Act & Assert (Действие и Проверка)
        with pytest.raises(argument_exception):
            conv.convert("", dt)

        with pytest.raises(argument_exception):
            conv.convert(None, dt)

    def test_fail_datetime_convertor_convert_invalid_type_raises(self):
        """
        Ожидание: Исключение argument_exception при передаче не даты (строка, число, None).
        Метод: datetime_convertor.convert
        Описание: Проверяет валидацию типа конвертируемого объекта.
        """
        # Arrange (Подготовка)
        conv = datetime_convertor()

        # Act & Assert (Действие и Проверка)
        with pytest.raises(argument_exception):
            conv.convert("date", "2026-10-21")

        with pytest.raises(argument_exception):
            conv.convert("date", 12345678)

        with pytest.raises(argument_exception):
            conv.convert("date", None)

    def test_success_datetime_convertor_convert_composite_object_with_date(self):
        """
        Ожидание: Извлечение свойств даты и времени из составного объекта при вызове с одним аргументом.
        Метод: datetime_convertor.convert
        Описание: Проверяет извлечение свойства created в формате ISO 8601 из объекта-стаба.
        """
        # Arrange (Подготовка)
        class dated_stub:
            @property
            def created(self) -> datetime:
                return datetime(2026, 10, 21, 12, 30)

            @property
            def name(self) -> str:
                return "заглушка"

        conv = datetime_convertor()

        # Act (Действие)
        res = conv.convert(dated_stub())

        # Assert (Проверка)
        assert res == {"created": "2026-10-21T12:30:00"}

    def test_success_datetime_convertor_convert_composite_object_without_date_returns_empty(self):
        """
        Ожидание: Возврат пустого словаря при отсутствии свойств даты в переданном составном объекте.
        Метод: datetime_convertor.convert
        Описание: Проверяет, что у модели без дат (range_model) результат конвертации пустой.
        """
        # Arrange (Подготовка)
        conv = datetime_convertor()
        kg = range_model("кг", 1000, None)

        # Act (Действие)
        res = conv.convert(kg)

        # Assert (Проверка)
        assert res == {}


class TestReferenceConvertor:
    """
    Набор модульных тестов для конвертера ссылочных доменных моделей reference_convertor
    """

    def test_success_reference_convertor_convert_group_model(self):
        """
        Ожидание: Преобразование модели группы номенклатуры в словарь полей.
        Метод: reference_convertor.convert
        Описание: Проверяет извлечение свойств id и name.
        """
        # Arrange (Подготовка)
        conv = reference_convertor()
        group = nomenclature_group_model("Сырье")

        # Act (Действие)
        res = conv.convert("group", group)

        # Assert (Проверка)
        assert "group" in res
        assert res["group"]["id"] == group.id
        assert res["group"]["name"] == "Сырье"

    def test_success_reference_convertor_convert_without_field_name(self):
        """
        Ожидание: Возврат плоского словаря модели при пустом имени поля.
        Метод: reference_convertor.convert
        Описание: Проверяет конвертацию без оборачивания во внешний ключ.
        """
        # Arrange (Подготовка)
        conv = reference_convertor()
        group = nomenclature_group_model("Сырье")

        # Act (Действие)
        res = conv.convert("", group)

        # Assert (Проверка)
        assert res["id"] == group.id
        assert res["name"] == "Сырье"

    def test_success_reference_convertor_convert_nested_range_model(self):
        """
        Ожидание: Корректная сериализация вложенной модели единицы измерения base_range.
        Метод: reference_convertor.convert
        Описание: Проверяет рекурсивное преобразование кг -> грамм.
        """
        # Arrange (Подготовка)
        conv = reference_convertor()
        gram = range_model("грамм", 1, None)
        kg = range_model("кг", 1000, gram)

        # Act (Действие)
        res = conv.convert("unit", kg)

        # Assert (Проверка)
        unit_data = res["unit"]
        assert unit_data["id"] == kg.id
        assert unit_data["name"] == "кг"
        assert unit_data["conversion_factor"] == 1000
        assert unit_data["base_range"] is not None
        assert unit_data["base_range"]["id"] == gram.id
        assert unit_data["base_range"]["name"] == "грамм"
        assert unit_data["base_range"]["base_range"] is None

    def test_success_reference_convertor_convert_nomenclature_model(self):
        """
        Ожидание: Корректная сериализация модели номенклатуры со связанной группой и единицей.
        Метод: reference_convertor.convert
        Описание: Проверяет извлечение всех связанных ссылочных объектов модели.
        """
        # Arrange (Подготовка)
        conv = reference_convertor()
        group = nomenclature_group_model("Молочные")
        unit = range_model("литр", 1, None)
        item = nomenclature_model("Молоко", "Молоко пастеризованное 3.2%", group, unit)

        # Act (Действие)
        res = conv.convert("item", item)

        # Assert (Проверка)
        data = res["item"]
        assert data["id"] == item.id
        assert data["name"] == "Молоко"
        assert data["full_name"] == "Молоко пастеризованное 3.2%"
        assert data["group"]["name"] == "Молочные"
        assert data["range"]["name"] == "литр"

    def test_success_reference_convertor_convert_storage_model(self):
        """
        Ожидание: Сериализация модели склада со свойствами name и address.
        Метод: reference_convertor.convert
        Описание: Проверяет преобразование storage_model.
        """
        # Arrange (Подготовка)
        conv = reference_convertor()
        storage = storage_model("Основной склад", "ул. Ленина, 1")

        # Act (Действие)
        res = conv.convert("storage", storage)

        # Assert (Проверка)
        assert res["storage"]["name"] == "Основной склад"
        assert res["storage"]["address"] == "ул. Ленина, 1"

    def test_success_reference_convertor_circular_reference_protection(self):
        """
        Ожидание: Разрыв циклической рекурсии и исключение RecursionError.
        Метод: reference_convertor.convert
        Описание: Проверяет возврат краткой ссылки {id, name} при обнаружении посещенного объекта.
        """
        # Arrange (Подготовка)
        conv = reference_convertor()
        r1 = range_model("r1")
        r2 = range_model("r2")
        r1.base_range = r2
        r2.base_range = r1

        # Act (Действие)
        res = conv.convert("r1", r1)

        # Assert (Проверка)
        assert res["r1"]["name"] == "r1"
        assert res["r1"]["base_range"]["name"] == "r2"
        assert res["r1"]["base_range"]["base_range"]["id"] == r1.id
        assert res["r1"]["base_range"]["base_range"]["name"] == "r1"

    def test_fail_reference_convertor_convert_invalid_obj_type_raises(self):
        """
        Ожидание: Исключение argument_exception при передаче объекта, не наследующего abstract_model.
        Метод: reference_convertor.convert
        Описание: Проверяет типобезопасность конвертера ссылочных типов.
        """
        # Arrange (Подготовка)
        conv = reference_convertor()

        # Act & Assert (Действие и Проверка)
        with pytest.raises(argument_exception):
            conv.convert("model", "not a model")

        with pytest.raises(argument_exception):
            conv.convert("model", 123)

        with pytest.raises(argument_exception):
            conv.convert("model", None)

    def test_success_reference_convertor_single_argument_calls(self):
        """
        Ожидание: Корректная конвертация при передаче только одного аргумента (объекта).
        Метод: reference_convertor.convert
        Описание: Проверяет гибкость сигнатуры вызова конвертеров с одним параметром.
        """
        # Arrange (Подготовка)
        b_conv = basic_convertor()
        dt_conv = datetime_convertor()
        r_conv = reference_convertor()
        d = date(2026, 10, 21)
        group = nomenclature_group_model("Группа тестовая")

        # Act & Assert (Действие и Проверка)
        assert b_conv.convert(100) == {"value": 100}
        assert b_conv.convert("abc") == {"value": "abc"}
        assert dt_conv.convert(d) == {"value": "2026-10-21"}

        res = r_conv.convert(group)
        assert res["name"] == "Группа тестовая"
        assert "id" in res

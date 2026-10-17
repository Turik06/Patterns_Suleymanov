import pytest
from Src.Core.exception import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.response_format_dto import response_format_dto
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report
from Src.Logics.text_report import text_report
from Src.Logics.rtf_report import rtf_report
from Src.Models.settings_model import settings_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


@pytest.fixture
def sample_range():
    """Единица измерения: килограмм с базовой грамм."""
    return range_model.create_kilogram()


@pytest.fixture
def sample_nomenclature(sample_range):
    """Номенклатура: Мука пшеничная."""
    group = nomenclature_group_model.create_grocery()
    return nomenclature_model.create_flour(group, sample_range)


@pytest.fixture
def sample_recipe(sample_range, sample_nomenclature):
    """Рецепт с двумя строками ингредиентов."""
    recipe = recipe_model("Блинчики")
    group = sample_nomenclature.group
    gram = sample_range.base
    sugar = nomenclature_model.create_sugar(group, gram)

    row1 = recipe_row_model(sample_nomenclature, 100.0, 95.0, sample_range)
    row2 = recipe_row_model(sugar, 20.0, 20.0, gram)
    recipe.add_row(row1)
    recipe.add_row(row2)
    return recipe


def test_success_convert_report_type_strings_and_aliases():
    """Проверка разрешения типов отчетов по строковым именам и алиасам через settings_manager."""
    assert settings_manager.convert_report_type("csv") == report_type_enum.CSV
    assert settings_manager.convert_report_type("CSV") == report_type_enum.CSV
    assert settings_manager.convert_report_type("md") == report_type_enum.MARKDOWN
    assert settings_manager.convert_report_type("markdown") == report_type_enum.MARKDOWN
    assert settings_manager.convert_report_type("xml") == report_type_enum.XML
    assert settings_manager.convert_report_type("html") == report_type_enum.HTML
    assert settings_manager.convert_report_type("txt") == report_type_enum.TXT
    assert settings_manager.convert_report_type("text") == report_type_enum.TXT
    assert settings_manager.convert_report_type("rtf") == report_type_enum.RTF


def test_success_convert_report_type_from_other_enum():
    """Проверка разрешения типов отчетов из значений response_format_dto через settings_manager."""
    assert settings_manager.convert_report_type(response_format_dto.CSV) == report_type_enum.CSV
    assert settings_manager.convert_report_type(response_format_dto.MARKDOWN) == report_type_enum.MARKDOWN
    assert settings_manager.convert_report_type(response_format_dto.XML) == report_type_enum.XML
    assert settings_manager.convert_report_type(response_format_dto.HTML) == report_type_enum.HTML
    assert settings_manager.convert_report_type(response_format_dto.TXT) == report_type_enum.TXT
    assert settings_manager.convert_report_type(response_format_dto.RTF) == report_type_enum.RTF


def test_fail_convert_report_type_invalid():
    """Проверка генерации исключения при некорректном или пустом типе отчета."""
    with pytest.raises(argument_exception):
        settings_manager.convert_report_type(None)
    with pytest.raises(argument_exception):
        settings_manager.convert_report_type("unsupported_format")


def test_success_factory_create_all_types():
    """Проверка создания фабрикой экземпляров всех поддерживаемых форматов отчетов."""
    factory = report_factory()
    assert isinstance(factory.create("csv"), csv_report)
    assert isinstance(factory.create("md"), markdown_report)
    assert isinstance(factory.create("markdown"), markdown_report)
    assert isinstance(factory.create("xml"), xml_report)
    assert isinstance(factory.create("html"), html_report)
    assert isinstance(factory.create("txt"), text_report)
    assert isinstance(factory.create("rtf"), rtf_report)


def test_success_factory_create_default():
    """Проверка создания отчета по умолчанию на основе настроек settings_model."""
    settings = settings_model()
    factory = report_factory(settings=settings)

    settings.response_format = "csv"
    assert isinstance(factory.create_default(), csv_report)

    settings.response_format = "markdown"
    assert isinstance(factory.create_default(), markdown_report)

    settings.response_format = "xml"
    assert isinstance(factory.create_default(), xml_report)

    settings.response_format = "html"
    assert isinstance(factory.create_default(), html_report)

    settings.response_format = "txt"
    assert isinstance(factory.create_default(), text_report)

    settings.response_format = "rtf"
    assert isinstance(factory.create_default(), rtf_report)


def test_success_recipe_csv_report(sample_recipe):
    """Проверка формирования бинарного CSV-отчета по рецепту."""
    report = csv_report()
    assert report.is_binary is True
    assert report.mime_type == "text/csv"
    assert report.extension == "csv"

    result = report.build(sample_recipe)
    assert isinstance(result, report_result_dto)
    assert len(result.binary) > 0
    assert result.text == ""

    text = bytes(result.binary).decode("utf-8")
    assert "Код;Наименование;Брутто;Нетто" in text
    assert "Мука пшеничная" in text
    assert "100.0;95.0" in text
    assert "Сахар" in text
    assert "20.0;20.0" in text


def test_success_recipe_markdown_report(sample_recipe):
    """Проверка формирования бинарного Markdown-отчета по рецепту."""
    report = markdown_report()
    assert report.is_binary is True
    assert report.mime_type == "text/markdown"
    assert report.extension == "md"

    result = report.build(sample_recipe)
    assert isinstance(result, report_result_dto)
    assert len(result.binary) > 0
    assert result.text == ""

    text = bytes(result.binary).decode("utf-8")
    assert "| Код | Наименование | Брутто | Нетто |" in text
    assert "| --- | --- | --- | --- |" in text
    assert "Мука пшеничная" in text
    assert "100.0 | 95.0" in text


def test_success_recipe_xml_report(sample_recipe):
    """Проверка формирования структурированного XML-отчета по рецепту."""
    report = xml_report()
    assert report.is_binary is False
    assert report.mime_type == "application/xml"
    assert report.extension == "xml"

    result = report.build(sample_recipe)
    assert isinstance(result, report_result_dto)
    assert result.text != ""
    assert len(result.binary) == 0

    assert '<?xml version="1.0" encoding="utf-8"?>' in result.text
    assert "<recipe>" in result.text
    assert f"<name>{sample_recipe.name}</name>" in result.text
    assert "<items>" in result.text
    assert "<item>" in result.text
    assert "<name>Мука пшеничная</name>" in result.text
    assert "<brutto>100.0</brutto>" in result.text
    assert "<netto>95.0</netto>" in result.text


def test_success_recipe_html_report(sample_recipe):
    """Проверка формирования HTML-отчета по рецепту."""
    report = html_report()
    assert report.is_binary is False
    assert report.mime_type == "text/html"
    assert report.extension == "html"

    result = report.build(sample_recipe)
    assert isinstance(result, report_result_dto)
    assert result.text != ""
    assert len(result.binary) == 0

    assert '<table border="1">' in result.text
    assert "<th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th>" in result.text
    assert "<td>Мука пшеничная</td><td>100.0</td><td>95.0</td>" in result.text


def test_success_recipe_text_report(sample_recipe):
    """Проверка формирования текстового отчета по рецепту."""
    report = text_report()
    assert report.is_binary is False
    assert report.mime_type == "text/plain"
    assert report.extension == "txt"

    result = report.build(sample_recipe)
    assert isinstance(result, report_result_dto)
    assert "Код | Наименование | Брутто | Нетто" in result.text
    assert "Мука пшеничная | 100.0 | 95.0" in result.text


def test_success_recipe_rtf_report(sample_recipe):
    """Проверка формирования RTF-отчета по рецепту."""
    report = rtf_report()
    assert report.is_binary is True
    assert report.mime_type == "application/rtf"
    assert report.extension == "rtf"

    result = report.build(sample_recipe)
    assert isinstance(result, report_result_dto)
    text = bytes(result.binary).decode("utf-8")
    assert r"{\rtf1\ansi\deff0" in text
    assert "Мука пшеничная" in text


def test_fail_build_none_source_raises_argument_exception():
    """Проверка генерации исключения при передаче None в качестве источника отчета."""
    for report_cls in (csv_report, markdown_report, xml_report, html_report, text_report, rtf_report):
        with pytest.raises(argument_exception):
            report_cls().build(None)


def test_fail_build_unsupported_source_raises_argument_exception():
    """Проверка генерации исключения при передаче неподдерживаемого типа объекта."""
    for report_cls in (csv_report, markdown_report, xml_report, html_report, text_report, rtf_report):
        with pytest.raises(argument_exception):
            report_cls().build("unsupported_string_source")

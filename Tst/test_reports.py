import pytest
from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Core.exception import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.report_type_dto import report_type_dto, ReportTypeEnum
from Src.Logics.report_factory import report_factory, ReportFactory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.text_report import text_report, TextReport
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.xml_report import xml_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.rtf_report import rtf_report
from Src.Models.settings_model import settings_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


@pytest.fixture
def sample_recipe():
    """Тестовый рецепт с ингредиентами."""
    group = nomenclature_group_model.create_grocery()
    gram = range_model.create_gram()
    flour = nomenclature_model.create_flour(group, gram)
    sugar = nomenclature_model.create_sugar(group, gram)

    recipe = recipe_model("Блинчики классические")
    row_flour = recipe_row_model(flour, 100.0, 95.0, gram)
    row_sugar = recipe_row_model(sugar, 20.0, 20.0, gram)
    recipe.add_row(row_flour)
    recipe.add_row(row_sugar)
    return recipe


def test_success_report_factory_create_text_report():
    """Проверка создания текстового отчета через фабрику."""
    factory = report_factory()
    report = factory.create(report_type_enum.TXT)

    assert report is not None
    assert isinstance(report, abstract_report)
    assert isinstance(report, text_report)


def test_success_report_factory_create_all_types():
    """Проверка создания фабрикой экземпляров всех поддерживаемых форматов."""
    factory = report_factory()
    assert isinstance(factory.create(report_type_enum.TXT), text_report)
    assert isinstance(factory.create(report_type_enum.CSV), csv_report)
    assert isinstance(factory.create(report_type_enum.HTML), html_report)
    assert isinstance(factory.create(report_type_enum.XML), xml_report)
    assert isinstance(factory.create(report_type_enum.MARKDOWN), markdown_report)
    assert isinstance(factory.create(report_type_enum.RTF), rtf_report)

    # Проверка создания по строковым идентификаторам
    assert isinstance(factory.create("txt"), text_report)
    assert isinstance(factory.create("csv"), csv_report)
    assert isinstance(factory.create("html"), html_report)
    assert isinstance(factory.create("xml"), xml_report)
    assert isinstance(factory.create("markdown"), markdown_report)
    assert isinstance(factory.create("md"), markdown_report)
    assert isinstance(factory.create("rtf"), rtf_report)


def test_success_report_factory_create_default():
    """Проверка создания отчета по умолчанию из настроек."""
    settings = settings_model()
    settings.response_format = report_type_enum.CSV
    factory = report_factory(settings=settings)

    report = factory.create_default()
    assert isinstance(report, csv_report)

    settings.response_format = "html"
    report_html = factory.create_default()
    assert isinstance(report_html, html_report)


def test_fail_report_factory_create_unsupported_type_raises_argument_exception():
    """Проверка выброса исключения при нереализованном типе отчета."""
    factory = report_factory()
    with pytest.raises(argument_exception):
        factory.create("UNSUPPORTED_TYPE")

    with pytest.raises(argument_exception):
        factory.create(None)


def test_template_method_steps_text_report(sample_recipe):
    """Проверка шагов шаблонного метода (заголовок, тело, подвал) для текстового отчета."""
    report = text_report()

    header = report.build_header(sample_recipe)
    body = report.build_body(sample_recipe)
    footer = report.build_footer(sample_recipe)
    result = report.build(sample_recipe)

    assert "Код | Наименование | Брутто | Нетто" in header
    assert "Мука пшеничная | 100.0 | 95.0" in body
    assert footer == ""
    assert isinstance(result, report_result_dto)
    assert result.text != ""
    assert "Мука пшеничная | 100.0 | 95.0" in result.text


def test_template_method_steps_html_report(sample_recipe):
    """
    Проверка шагов шаблонного метода для HTML отчета:
    - Сформировать заголовок (таблица + thead)
    - Сформировать табличную часть (tbody + строки)
    - Сформировать подвал (закрывающие теги)
    """
    report = html_report()

    header = report.build_header(sample_recipe)
    body = report.build_body(sample_recipe)
    footer = report.build_footer(sample_recipe)
    result = report.build(sample_recipe)

    assert '<table border="1">' in header
    assert "<th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th>" in header
    assert "<td>Мука пшеничная</td><td>100.0</td><td>95.0</td>" in body
    assert "</tbody>\n</table>" in footer

    assert isinstance(result, report_result_dto)
    assert '<table border="1">' in result.text
    assert "<td>Мука пшеничная</td>" in result.text
    assert "</table>" in result.text


def test_template_method_steps_csv_report(sample_recipe):
    """Проверка шагов шаблонного метода для CSV отчета (бинарный результат)."""
    report = csv_report()

    header = report.build_header(sample_recipe)
    body = report.build_body(sample_recipe)
    footer = report.build_footer(sample_recipe)
    result = report.build(sample_recipe)

    assert "Код;Наименование;Брутто;Нетто" in header
    assert "Мука пшеничная;100.0;95.0" in body
    assert footer == ""

    assert isinstance(result, report_result_dto)
    assert len(result.binary) > 0
    text = bytes(result.binary).decode("utf-8")
    assert "Код;Наименование;Брутто;Нетто" in text
    assert "Мука пшеничная;100.0;95.0" in text


def test_template_method_steps_xml_report(sample_recipe):
    """
    Проверка шагов шаблонного метода для XML отчета:
    - Заголовок (декларация и тег recipe)
    - Табличная часть (элементы item)
    - Подвал (закрывающие теги items и recipe)
    """
    report = xml_report()

    header = report.build_header(sample_recipe)
    body = report.build_body(sample_recipe)
    footer = report.build_footer(sample_recipe)
    result = report.build(sample_recipe)

    assert '<?xml version="1.0" encoding="utf-8"?>' in header
    assert "<recipe>" in header
    assert f"<name>{sample_recipe.name}</name>" in header

    assert "<item>" in body
    assert "<name>Мука пшеничная</name>" in body
    assert "<brutto>100.0</brutto>" in body

    assert "</items>\n</recipe>" in footer

    assert isinstance(result, report_result_dto)
    assert "<recipe>" in result.text
    assert "<name>Мука пшеничная</name>" in result.text
    assert "</recipe>" in result.text


def test_template_method_steps_markdown_report(sample_recipe):
    """Проверка шагов шаблонного метода для Markdown отчета."""
    report = markdown_report()

    header = report.build_header(sample_recipe)
    body = report.build_body(sample_recipe)
    footer = report.build_footer(sample_recipe)
    result = report.build(sample_recipe)

    assert "| Код | Наименование | Брутто | Нетто |" in header
    assert "| --- | --- | --- | --- |" in header
    assert "Мука пшеничная | 100.0 | 95.0" in body
    assert footer == ""

    assert isinstance(result, report_result_dto)
    text = bytes(result.binary).decode("utf-8")
    assert "| Код | Наименование | Брутто | Нетто |" in text


def test_template_method_steps_rtf_report(sample_recipe):
    """Проверка шагов шаблонного метода для RTF отчета."""
    report = rtf_report()

    header = report.build_header(sample_recipe)
    body = report.build_body(sample_recipe)
    footer = report.build_footer(sample_recipe)
    result = report.build(sample_recipe)

    assert r"{\rtf1\ansi\deff0" in header
    assert "Мука пшеничная" in body
    assert "}" in footer

    assert isinstance(result, report_result_dto)
    text = bytes(result.binary).decode("utf-8")
    assert r"{\rtf1\ansi\deff0" in text


def test_fail_abstract_report_none_source():
    """Проверка выброса исключения при передаче None в build()."""
    report = text_report()
    with pytest.raises(argument_exception):
        report.build(None)


def test_fail_abstract_report_invalid_source_type():
    """Проверка выброса исключения при передаче объекта некорректного типа в build()."""
    report = text_report()
    with pytest.raises(argument_exception):
        report.build("invalid_source_string")


def test_success_settings_manager_convert_report_type():
    """Проверка работы метода convert_report_type в settings_manager."""
    assert settings_manager.convert_report_type("csv") == report_type_enum.CSV
    assert settings_manager.convert_report_type("CSV") == report_type_enum.CSV
    assert settings_manager.convert_report_type("html") == report_type_enum.HTML
    assert settings_manager.convert_report_type("txt") == report_type_enum.TXT
    assert settings_manager.convert_report_type("text") == report_type_enum.TXT
    assert settings_manager.convert_report_type("markdown") == report_type_enum.MARKDOWN
    assert settings_manager.convert_report_type("md") == report_type_enum.MARKDOWN
    assert settings_manager.convert_report_type("xml") == report_type_enum.XML
    assert settings_manager.convert_report_type("rtf") == report_type_enum.RTF
    assert settings_manager.convert_report_type(report_type_enum.HTML) == report_type_enum.HTML
    assert settings_manager.convert_report_type(1) == report_type_enum.TXT


def test_fail_settings_manager_convert_report_type_invalid():
    """Проверка выброса исключения при некорректном формате в convert_report_type."""
    with pytest.raises(argument_exception):
        settings_manager.convert_report_type(None)

    with pytest.raises(argument_exception):
        settings_manager.convert_report_type("UNSUPPORTED_123")

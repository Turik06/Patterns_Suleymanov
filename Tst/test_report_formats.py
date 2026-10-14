import pytest
from Src.Core.exception import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_dto import report_type_dto
from Src.Dtos.response_format_dto import response_format_dto
from Src.Logics.report_factory import report_factory
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report
from Src.Logics.text_report import text_report
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


def test_success_report_type_from_any_strings_and_aliases():
    """
    <summary>
    Проверка разрешения типов отчетов по строковым именам и алиасам.
    </summary>
    <description>
    Arrange: Набор строковых названий и алиасов (csv, md, markdown, xml, html, txt, text).
    Act: Вызов report_type_dto.from_any().
    Assert: Возвращается соответствующий элемент перечисления report_type_dto.
    </description>
    """
    assert report_type_dto.from_any("csv") == report_type_dto.CSV
    assert report_type_dto.from_any("CSV") == report_type_dto.CSV
    assert report_type_dto.from_any("md") == report_type_dto.MARKDOWN
    assert report_type_dto.from_any("markdown") == report_type_dto.MARKDOWN
    assert report_type_dto.from_any("xml") == report_type_dto.XML
    assert report_type_dto.from_any("html") == report_type_dto.HTML
    assert report_type_dto.from_any("txt") == report_type_dto.TXT
    assert report_type_dto.from_any("text") == report_type_dto.TXT


def test_success_report_type_from_any_other_enum():
    """
    <summary>
    Проверка разрешения типов отчетов из значений response_format_dto.
    </summary>
    <description>
    Arrange: Значения response_format_dto (CSV, MARKDOWN, XML, HTML, TXT).
    Act: Вызов report_type_dto.from_any().
    Assert: Корректно преобразуются в элементы report_type_dto.
    </description>
    """
    assert report_type_dto.from_any(response_format_dto.CSV) == report_type_dto.CSV
    assert report_type_dto.from_any(response_format_dto.MARKDOWN) == report_type_dto.MARKDOWN
    assert report_type_dto.from_any(response_format_dto.XML) == report_type_dto.XML
    assert report_type_dto.from_any(response_format_dto.HTML) == report_type_dto.HTML
    assert report_type_dto.from_any(response_format_dto.TXT) == report_type_dto.TXT


def test_fail_report_type_from_any_invalid():
    """
    <summary>
    Проверка генерации исключения при некорректном или пустом типе отчета.
    </summary>
    <description>
    Arrange: None и неподдерживаемая строка.
    Act: Вызов report_type_dto.from_any().
    Assert: Выбрасывается argument_exception.
    </description>
    """
    with pytest.raises(argument_exception):
        report_type_dto.from_any(None)
    with pytest.raises(argument_exception):
        report_type_dto.from_any("unsupported_format")


def test_success_factory_create_all_types():
    """
    <summary>
    Проверка создания фабрикой экземпляров всех поддерживаемых форматов отчетов.
    </summary>
    <description>
    Arrange: Фабрика отчетов report_factory.
    Act: Вызовы factory.create() для csv, md, markdown, xml, html, txt.
    Assert: Созданные объекты соответствуют целевым классам отчетов.
    </description>
    """
    factory = report_factory()
    assert isinstance(factory.create("csv"), csv_report)
    assert isinstance(factory.create("md"), markdown_report)
    assert isinstance(factory.create("markdown"), markdown_report)
    assert isinstance(factory.create("xml"), xml_report)
    assert isinstance(factory.create("html"), html_report)
    assert isinstance(factory.create("txt"), text_report)


def test_success_factory_create_default():
    """
    <summary>
    Проверка создания отчета по умолчанию на основе настроек settings_model.
    </summary>
    <description>
    Arrange: Фабрика с инкапсулированными настройками settings_model.
    Act: Смена response_format в настройках и вызовы factory.create_default().
    Assert: Возвращается экземпляр отчета, соответствующий текущим настройкам.
    </description>
    """
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


def test_success_recipe_csv_report(sample_recipe):
    """
    <summary>
    Проверка формирования бинарного CSV-отчета по рецепту.
    </summary>
    <description>
    Arrange: Тестовый рецепт sample_recipe.
    Act: Вызов csv_report.build(sample_recipe).
    Assert: Результат бинарный (UTF-8), содержит заголовки через ';' и строки ингредиентов.
    </description>
    """
    report = csv_report()
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
    """
    <summary>
    Проверка формирования бинарного Markdown-отчета по рецепту.
    </summary>
    <description>
    Arrange: Тестовый рецепт sample_recipe.
    Act: Вызов markdown_report.build(sample_recipe).
    Assert: Результат бинарный, содержит таблицу Markdown с заголовками и строками ингредиентов.
    </description>
    """
    report = markdown_report()
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
    """
    <summary>
    Проверка формирования структурированного XML-отчета по рецепту.
    </summary>
    <description>
    Arrange: Тестовый рецепт sample_recipe.
    Act: Вызов xml_report.build(sample_recipe).
    Assert: Результат текстовый, содержит XML-декларацию, тег <recipe>, элементы <item> и данные ингредиентов.
    </description>
    """
    report = xml_report()
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
    """
    <summary>
    Проверка формирования HTML-отчета по рецепту в виде чистой таблицы.
    </summary>
    <description>
    Arrange: Тестовый рецепт sample_recipe.
    Act: Вызов html_report.build(sample_recipe).
    Assert: Результат текстовый, содержит тег таблицы table border='1', thead, tbody и ячейки th/td.
    </description>
    """
    report = html_report()
    result = report.build(sample_recipe)

    assert isinstance(result, report_result_dto)
    assert result.text != ""
    assert len(result.binary) == 0

    assert '<table border="1">' in result.text
    assert "<th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th>" in result.text
    assert "<td>Мука пшеничная</td><td>100.0</td><td>95.0</td>" in result.text


def test_success_recipe_text_report(sample_recipe):
    """
    <summary>
    Проверка формирования плоского текстового отчета по рецепту.
    </summary>
    <description>
    Arrange: Тестовый рецепт sample_recipe.
    Act: Вызов text_report.build(sample_recipe).
    Assert: Результат текстовый, строки и колонки разделены вертикальной чертой.
    </description>
    """
    report = text_report()
    result = report.build(sample_recipe)

    assert isinstance(result, report_result_dto)
    assert "Код | Наименование | Брутто | Нетто" in result.text
    assert "Мука пшеничная | 100.0 | 95.0" in result.text


def test_success_nomenclature_reports_content(sample_nomenclature):
    """
    <summary>
    Проверка корректности формирования карточки номенклатуры во всех 5 форматах.
    </summary>
    <description>
    Arrange: Экземпляр номенклатуры sample_nomenclature.
    Act: Построение отчетов через CSV, Markdown, XML, HTML, TXT.
    Assert: Данные номенклатуры (наименование, группа, ед. изм.) корректно представлены во всех форматах.
    </description>
    """
    # CSV
    csv_res = csv_report().build(sample_nomenclature)
    csv_text = bytes(csv_res.binary).decode("utf-8")
    assert "Код;Наименование;Полное наименование;Группа;Единица измерения" in csv_text
    assert "Мука пшеничная" in csv_text
    assert "Бакалея" in csv_text

    # Markdown
    md_res = markdown_report().build(sample_nomenclature)
    md_text = bytes(md_res.binary).decode("utf-8")
    assert "| Поле | Значение |" in md_text
    assert "| Полное наименование | Мука пшеничная высший сорт |" in md_text

    # XML
    xml_res = xml_report().build(sample_nomenclature)
    assert "<nomenclature>" in xml_res.text
    assert "<name>Мука пшеничная</name>" in xml_res.text
    assert "<group>Бакалея</group>" in xml_res.text

    # HTML
    html_res = html_report().build(sample_nomenclature)
    assert '<table border="1">' in html_res.text
    assert "<td>Полное наименование</td><td>Мука пшеничная высший сорт</td>" in html_res.text

    # TXT
    txt_res = text_report().build(sample_nomenclature)
    assert "Наименование: Мука пшеничная" in txt_res.text
    assert "Группа: Бакалея" in txt_res.text


def test_success_range_reports_content(sample_range):
    """
    <summary>
    Проверка корректности формирования карточки единицы измерения во всех 5 форматах.
    </summary>
    <description>
    Arrange: Экземпляр единицы измерения sample_range.
    Act: Построение отчетов через CSV, Markdown, XML, HTML, TXT.
    Assert: Данные единицы (коэффициент, базовая единица) корректно представлены во всех форматах.
    </description>
    """
    # CSV
    csv_res = csv_report().build(sample_range)
    csv_text = bytes(csv_res.binary).decode("utf-8")
    assert "Код;Наименование;Коэффициент;Базовая единица" in csv_text
    assert "килограмм;1000;грамм" in csv_text

    # Markdown
    md_res = markdown_report().build(sample_range)
    md_text = bytes(md_res.binary).decode("utf-8")
    assert "| Поле | Значение |" in md_text
    assert "| Коэффициент | 1000 |" in md_text
    assert "| Базовая единица | грамм |" in md_text

    # XML
    xml_res = xml_report().build(sample_range)
    assert "<range>" in xml_res.text
    assert "<name>килограмм</name>" in xml_res.text
    assert "<conversion_factor>1000</conversion_factor>" in xml_res.text
    assert "<base_unit>грамм</base_unit>" in xml_res.text

    # HTML
    html_res = html_report().build(sample_range)
    assert '<table border="1">' in html_res.text
    assert "<td>Коэффициент</td><td>1000</td>" in html_res.text

    # TXT
    txt_res = text_report().build(sample_range)
    assert "Наименование: килограмм" in txt_res.text
    assert "Коэффициент: 1000" in txt_res.text
    assert "Базовая единица: грамм" in txt_res.text


def test_fail_build_none_source_raises_argument_exception():
    """
    <summary>
    Проверка генерации исключения при передаче None в качестве источника отчета.
    </summary>
    <description>
    Arrange: Классы отчетов всех форматов.
    Act: Вызов build(None).
    Assert: Для каждого класса выбрасывается argument_exception.
    </description>
    """
    for report_cls in (csv_report, markdown_report, xml_report, html_report, text_report):
        with pytest.raises(argument_exception):
            report_cls().build(None)


def test_fail_build_unsupported_source_raises_argument_exception():
    """
    <summary>
    Проверка генерации исключения при передаче неподдерживаемого типа объекта.
    </summary>
    <description>
    Arrange: Неподдерживаемый строковый объект.
    Act: Вызов build(unsupported_string).
    Assert: Для каждого класса выбрасывается argument_exception.
    </description>
    """
    for report_cls in (csv_report, markdown_report, xml_report, html_report, text_report):
        with pytest.raises(argument_exception):
            report_cls().build("unsupported_string_source")

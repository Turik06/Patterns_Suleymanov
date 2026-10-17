import pytest

flask = pytest.importorskip("flask")

from main import app, storage, settings, factory
from Src.Dtos.report_type_enum import report_type_enum
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


@pytest.fixture(scope="module")
def client():
    """Тестовый клиент Flask."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def setup_test_recipes():
    """Гарантирует наличие тестового рецепта в хранилище storage_manager."""
    if not storage.recipes:
        group = nomenclature_group_model.create_grocery()
        gram = range_model.create_gram()
        flour = nomenclature_model.create_flour(group, gram)
        sugar = nomenclature_model.create_sugar(group, gram)

        recipe = recipe_model("Блинчики интеграционные")
        recipe.add_row(recipe_row_model(flour, 150.0, 140.0, gram))
        recipe.add_row(recipe_row_model(sugar, 30.0, 30.0, gram))
        storage.recipes[recipe.unique_code] = recipe


def test_integration_get_report_endpoint(client):
    """Интеграционный тест GET /api/get_report: проверка дефолтного текстового отчета."""
    response = client.get("/api/get_report")
    assert response.status_code == 200
    assert "text/plain" in response.content_type
    data = response.data.decode("utf-8")
    assert "Код | Наименование | Брутто | Нетто" in data
    assert "Мука пшеничная" in data


def test_integration_report_format_html(client):
    """
    Интеграционный тест GET /api/report?format=html:
    проверка HTML отчета, MIME-типа text/html и структуры таблицы.
    """
    response = client.get("/api/report?format=html")
    assert response.status_code == 200
    assert "text/html" in response.content_type
    html_text = response.data.decode("utf-8")
    assert '<table border="1">' in html_text
    assert "<th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th>" in html_text
    assert "<td>Мука пшеничная</td>" in html_text
    assert "</table>" in html_text


def test_integration_report_format_csv_attachment(client):
    """
    Интеграционный тест GET /api/report?format=csv:
    проверка бинарного CSV отчета, MIME-типа text/csv и заголовка Content-Disposition.
    """
    response = client.get("/api/report?format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.content_type
    assert "attachment" in response.headers.get("Content-Disposition", "")
    assert ".csv" in response.headers.get("Content-Disposition", "")
    csv_text = response.data.decode("utf-8")
    assert "Код;Наименование;Брутто;Нетто" in csv_text
    assert "Мука пшеничная" in csv_text


def test_integration_report_format_markdown_attachment(client):
    """
    Интеграционный тест GET /api/report?format=markdown:
    проверка Markdown отчета, MIME-типа text/markdown и вложения.
    """
    response = client.get("/api/report?format=markdown")
    assert response.status_code == 200
    assert "text/markdown" in response.content_type
    assert "attachment" in response.headers.get("Content-Disposition", "")
    md_text = response.data.decode("utf-8")
    assert "| Код | Наименование | Брутто | Нетто |" in md_text
    assert "| --- | --- | --- | --- |" in md_text


def test_integration_report_format_xml(client):
    """
    Интеграционный тест GET /api/report?format=xml:
    проверка XML отчета, MIME-типа application/xml и элементов XML.
    """
    response = client.get("/api/report?format=xml")
    assert response.status_code == 200
    assert "application/xml" in response.content_type
    xml_text = response.data.decode("utf-8")
    assert '<?xml version="1.0" encoding="utf-8"?>' in xml_text
    assert "<recipe>" in xml_text
    assert "<items>" in xml_text
    assert "<name>Мука пшеничная</name>" in xml_text
    assert "</recipe>" in xml_text


def test_integration_report_format_rtf_attachment(client):
    """
    Интеграционный тест GET /api/report?format=rtf:
    проверка RTF отчета, MIME-типа application/rtf и вложения.
    """
    response = client.get("/api/report?format=rtf")
    assert response.status_code == 200
    assert "application/rtf" in response.content_type
    assert "attachment" in response.headers.get("Content-Disposition", "")
    rtf_text = response.data.decode("utf-8")
    assert r"{\rtf1" in rtf_text


def test_integration_report_default_from_settings(client):
    """
    Интеграционный тест GET /api/report/default:
    проверка использования формата из настроек settings_manager.
    """
    # Устанавливаем в настройках формат XML
    settings.settings.response_format = report_type_enum.XML
    response = client.get("/api/report/default")
    assert response.status_code == 200
    assert "application/xml" in response.content_type

    # Меняем в настройках формат на HTML
    settings.settings.response_format = report_type_enum.HTML
    response_html = client.get("/api/report/default")
    assert response_html.status_code == 200
    assert "text/html" in response_html.content_type


def test_integration_report_by_recipe_id(client):
    """
    Интеграционный тест GET /api/report/<recipe_id>/<format>:
    проверка получения отчета по конкретному идентификатору рецепта.
    """
    first_recipe = list(storage.recipes.values())[0]
    response = client.get(f"/api/report/{first_recipe.unique_code}/html")
    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert '<table border="1">' in response.data.decode("utf-8")


def test_integration_report_not_found(client):
    """Интеграционный тест ошибки 404 при запросе несуществующего рецепта."""
    response = client.get("/api/report/NON_EXISTENT_RECIPE_CODE_12345/txt")
    assert response.status_code == 404
    assert "не найден" in response.data.decode("utf-8")


def test_integration_report_unsupported_format(client):
    """Интеграционный тест ошибки 400 при указании неизвестного формата отчета."""
    response = client.get("/api/report?format=UNSUPPORTED_XYZ_FORMAT")
    assert response.status_code == 400
    assert "не реализован" in response.data.decode("utf-8")

import sys
import pytest
from pathlib import Path

# Определение корня проекта
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from main import app
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager


class TestApi:
    """
    Набор тестов для REST API приложения
    """

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """
        Инициализация тестового клиента Flask и изолированное наполнение хранилища
        """
        # Подготовка
        app.testing = True
        self.client = app.test_client()
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()
        self.settings = settings_manager()
        self.settings.settings.response_format = report_type_enum.MARKDOWN

    def test_success_get_healthcheck(self):
        """
        Проверка доступности базового проверочного эндпоинта /api/get_report
        """
        # Подготовка и Действие
        response = self.client.get("/api/get_report")

        # Проверка
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "success"

    def test_success_get_report_receipt_markdown_download(self):
        """
        Проверка выгрузки Markdown-отчета для рецепта в виде скачиваемого файла
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Блины классические?format=Markdown")

        # Проверка
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert ".md" in response.headers.get("Content-Disposition", "")
        content = response.data.decode("utf-8")
        assert "Масло сливочное" in content or "Тесто для блинов" in content

    def test_success_get_report_receipt_csv_download(self):
        """
        Проверка выгрузки CSV-отчета для рецепта в виде скачиваемого файла
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Блины классические?format=CSV")

        # Проверка
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert ".csv" in response.headers.get("Content-Disposition", "")
        content = response.data.decode("utf-8")
        assert "Код;Наименование" in content or "Масло сливочное" in content

    def test_success_get_report_receipt_xml_text(self):
        """
        Проверка структурированного XML-ответа для технологической карты
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Блины классические?format=XML")

        # Проверка
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("Content-Type", "")
        content = response.data.decode("utf-8")
        assert "<recipe" in content
        assert "Масло сливочное" in content or "Блины классические" in content

    def test_success_get_report_receipt_html_text(self):
        """
        Проверка структурированного HTML-ответа для технологической карты
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Блины классические?format=HTML")

        # Проверка
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        content = response.data.decode("utf-8")
        assert "<table" in content
        assert "Масло сливочное" in content or "Тесто для блинов" in content

    def test_success_get_report_nomenclature_csv_download(self):
        """
        Проверка выгрузки CSV-отчета для номенклатуры в виде скачиваемого файла
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/nomenclature/Мука пшеничная?format=CSV")

        # Проверка
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert ".csv" in response.headers.get("Content-Disposition", "")
        content = response.data.decode("utf-8")
        assert "Мука пшеничная" in content

    def test_success_get_report_range_xml_text(self):
        """
        Проверка выгрузки XML-отчета для единицы измерения
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/range/грамм?format=XML")

        # Проверка
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("Content-Type", "")
        content = response.data.decode("utf-8")
        assert "<range" in content
        assert "грамм" in content

    def test_success_get_report_default_endpoint(self):
        """
        Проверка эндпоинта /api/report/default/<entity_type>/<id> с форматом по умолчанию
        """
        # Подготовка
        self.settings.settings.response_format = report_type_enum.MARKDOWN

        # Действие
        response = self.client.get("/api/report/default/receipt/Блины классические")

        # Проверка
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert ".md" in response.headers.get("Content-Disposition", "")

    def test_fail_get_report_unknown_entity(self):
        """
        Проверка возврата ошибки 404 при запросе несуществующей сущности
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/НесуществующееБлюдо")

        # Проверка
        assert response.status_code == 404

    def test_fail_get_report_invalid_format(self):
        """
        Проверка возврата ошибки 400 при указании некорректного формата отчета
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Блины классические?format=INVALID_FORMAT")

        # Проверка
        assert response.status_code == 400

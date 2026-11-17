import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from main import app
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager


class TestApiCrud:
    """Интеграционные тесты для CRUD операций и Swagger"""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Настройка клиента и сброс хранилища перед каждым тестом"""
        app.testing = True
        self.client = app.test_client()
        self.storage = storage_manager()
        self.storage.first_start()

    def test_swagger_openapi_spec(self):
        """Проверка наличия файла спецификации OpenAPI"""
        openapi_file = repo_root / "openapi.yaml"
        assert openapi_file.exists() is True
        content = openapi_file.read_text(encoding="utf-8")
        assert "openapi: 3.0.0" in content
        assert "/api/entity/{entity_type}" in content

    def test_get_report_formats(self):
        """Проверка получения списка форматов отчетов"""
        response = self.client.get("/api/reports/formats")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert "CSV" in data
        assert "MARKDOWN" in data
        assert "HTML" in data

    def test_create_and_read_range(self):
        """Создание новой единицы измерения и ее чтение"""
        payload = {
            "name": "миллиграмм",
            "value": 1
        }
        create_res = self.client.put("/api/entity/range_model", json=payload)
        assert create_res.status_code == 201
        data = create_res.get_json()
        assert data["name"] == "миллиграмм"
        code = data["unique_code"]

        get_res = self.client.get(f"/api/entity/range_model/{code}")
        assert get_res.status_code == 200
        assert get_res.get_json()["name"] == "миллиграмм"

    def test_create_entity_post_method(self):
        """Создание склада через метод POST"""
        payload = {
            "name": "Склад №5"
        }
        res = self.client.post("/api/entity/storage_model", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["name"] == "Склад №5"

    def test_create_range_missing_base_fail(self):
        """Ошибка при создании единицы с несуществующей базовой единицей"""
        payload = {
            "name": "тонна",
            "value": 1000,
            "base_code": "unknown-base-code-999"
        }
        res = self.client.put("/api/entity/range_model", json=payload)
        assert res.status_code == 400
        assert "не найден" in res.get_json()["error"]

    def test_get_non_existent_entity_fail(self):
        """Ошибка 404 при запросе несуществующей сущности"""
        res = self.client.get("/api/entity/range_model/missing-code-123")
        assert res.status_code == 404

    def test_update_unlinked_entity(self):
        """Успешное обновление полей свободной сущности"""
        payload = {
            "name": "микрометр",
            "value": 1
        }
        create_res = self.client.put("/api/entity/range_model", json=payload)
        code = create_res.get_json()["unique_code"]

        update_res = self.client.patch(f"/api/entity/range_model/{code}", json={"name": "мкм"})
        assert update_res.status_code == 200
        assert update_res.get_json()["name"] == "мкм"

    def test_update_linked_entity_code_fail(self):
        """Запрет изменения кода связанной сущности"""
        gram = self.storage.get_range("грамм")
        res = self.client.patch(f"/api/entity/range_model/{gram.unique_code}", json={"unique_code": "new-code-999"})
        assert res.status_code == 409
        assert "Нельзя менять код" in res.get_json()["error"]
        assert "referrers" in res.get_json()

    def test_delete_unlinked_entity(self):
        """Успешное удаление несвязанной сущности"""
        payload = {
            "name": "Склад временный"
        }
        create_res = self.client.post("/api/entity/storage_model", json=payload)
        code = create_res.get_json()["unique_code"]

        del_res = self.client.delete(f"/api/entity/storage_model/{code}")
        assert del_res.status_code == 200
        assert del_res.get_json()["result"] == "success"

        check_res = self.client.get(f"/api/entity/storage_model/{code}")
        assert check_res.status_code == 404

    def test_delete_linked_range_fail(self):
        """Запрет удаления связанной единицы измерения"""
        gram = self.storage.get_range("грамм")
        res = self.client.delete(f"/api/entity/range_model/{gram.unique_code}")
        assert res.status_code == 409
        assert "связана с другими" in res.get_json()["error"]
        assert len(res.get_json()["referrers"]) > 0

    def test_delete_linked_group_fail(self):
        """Запрет удаления связанной группы номенклатуры"""
        group = list(self.storage.groups.values())[0]
        res = self.client.delete(f"/api/entity/group_model/{group.unique_code}")
        assert res.status_code == 409
        assert "связана с другими" in res.get_json()["error"]
        assert len(res.get_json()["referrers"]) > 0

    def test_delete_linked_nomenclature_fail(self):
        """Запрет удаления связанной номенклатуры"""
        nom = self.storage.get_nomenclature("Мука пшеничная")
        res = self.client.delete(f"/api/entity/nomenclature_model/{nom.unique_code}")
        assert res.status_code == 409
        assert "связана с другими" in res.get_json()["error"]
        assert len(res.get_json()["referrers"]) > 0

    def test_delete_missing_entity_fail(self):
        """Ошибка 404 при удалении несуществующей сущности"""
        res = self.client.delete("/api/entity/range_model/missing-code-000")
        assert res.status_code == 404

    def test_settings_manager_deserialization(self):
        """Проверка десериализации настроек через общий механизм"""
        sm = settings_manager()
        sm.load()
        assert sm.is_loaded is True
        assert sm.settings is not None
        assert sm.settings.organization is not None
        assert sm.settings.organization.name != ""
        assert sm.settings.boss_name != ""

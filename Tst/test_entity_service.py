import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Logics.entity_service import entity_service
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


class TestEntityService:
    """Тесты сервисного слоя entity_service"""

    @pytest.fixture(autouse=True)
    def setup_service(self):
        """Подготовка хранилища и сервиса"""
        self.storage = storage_manager()
        self.storage.first_start()
        self.service = entity_service(self.storage)

    def test_get_entity_success(self):
        """Успешное получение сущности по коду"""
        gram = self.storage.get_range("грамм")
        entity = self.service.get_entity("range_model", gram.unique_code)
        assert entity == gram

    def test_get_entity_not_found(self):
        """Ошибка при запросе несуществующей сущности"""
        with pytest.raises(LookupError):
            self.service.get_entity("range_model", "unknown-code-123")

    def test_create_and_delete_entity(self):
        """Создание и удаление новой сущности"""
        payload = {"name": "Новый склад 99"}
        model = self.service.create_entity("storage_model", payload)
        assert model.name == "Новый склад 99"

        # Удаление
        res = self.service.delete_entity("storage_model", model.unique_code)
        assert res is True

        with pytest.raises(LookupError):
            self.service.get_entity("storage_model", model.unique_code)

    def test_delete_linked_entity_fail(self):
        """Запрет удаления связанной сущности"""
        gram = self.storage.get_range("грамм")
        with pytest.raises(PermissionError):
            self.service.delete_entity("range_model", gram.unique_code)

    def test_update_linked_code_fail(self):
        """Запрет изменения кода связанной сущности"""
        gram = self.storage.get_range("грамм")
        with pytest.raises(PermissionError):
            self.service.update_entity("range_model", gram.unique_code, {"unique_code": "new-code-777"})

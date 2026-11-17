import pytest
from Src.Core.validator import operation_exception
from Src.Logics.storage_reposity import storage_repository
from Src.Logics.storage_manager import storage_manager
from Src.Logics.entity_service import entity_service
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.storage_model import storage_model


class TestStorageRepository:
    """Тесты репозитория storage_repository"""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = storage_repository()

    def test_registry_single_entity(self):
        """Регистрация одиночного объекта"""
        storage = storage_model("Склад сырья")
        self.repo.registry(storage)
        assert storage.unique_code in self.repo.data
        assert self.repo.counts[storage.unique_code] == 0
        assert self.repo.get(storage.unique_code) == storage
        assert self.repo.can_delete(storage) is True

    def test_registry_with_nested_attachments(self):
        """Регистрация объекта со вложенностями и учет счетчиков"""
        group = nomenclature_group_model("Бакалея")
        range_unit = range_model("кг", 1000)
        self.repo.registry(group)
        self.repo.registry(range_unit)

        nom = nomenclature_model("Мука", "Мука высший сорт", group, range_unit)
        self.repo.registry(nom)

        assert nom.unique_code in self.repo.data
        assert self.repo.counts[nom.unique_code] == 0
        assert self.repo.counts[group.unique_code] > 0
        assert self.repo.counts[range_unit.unique_code] > 0
        assert self.repo.can_delete(nom) is True
        assert self.repo.can_delete(group) is False
        assert self.repo.can_delete(range_unit) is False

    def test_registry_range(self):
        """Групповая регистрация списка объектов"""
        items = [
            storage_model("Склад 1"),
            storage_model("Склад 2"),
            storage_model("Склад 3"),
        ]
        self.repo.registry_range(items)
        assert len(self.repo.data) == 3

    def test_get_not_found(self):
        """Ошибка при поиске несуществующего кода"""
        with pytest.raises(operation_exception):
            self.repo.get("unknown-guid")

    def test_delete_unlinked_entity(self):
        """Успешное удаление несвязанной сущности"""
        storage = storage_model("Склад архивный")
        self.repo.registry(storage)
        assert self.repo.can_delete(storage) is True

        self.repo.delete(storage)
        assert storage.unique_code not in self.repo.data
        assert storage.unique_code not in self.repo.counts

    def test_delete_linked_entity_error(self):
        """Ошибка при попытке удалить связанную сущность"""
        group = nomenclature_group_model("Группа А")
        range_unit = range_model("шт", 1)
        self.repo.registry(group)
        self.repo.registry(range_unit)

        nom = nomenclature_model("Товар", "Товар полный", group, range_unit)
        self.repo.registry(nom)

        with pytest.raises(operation_exception):
            self.repo.delete(group)

    def test_clear_repository(self):
        """Очистка данных репозитория"""
        storage = storage_model("Склад")
        self.repo.registry(storage)
        assert len(self.repo.data) > 0

        self.repo.clear()
        assert len(self.repo.data) == 0
        assert len(self.repo.counts) == 0


class TestEntityServiceWithRepository:
    """Тесты интеграции entity_service и storage_repository"""

    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.storage = storage_manager()
        self.storage.first_start()
        self.service = entity_service(self.storage)

    def test_storage_has_repository(self):
        """Проверка наличия репозитория в хранилище"""
        assert self.storage.repository is not None
        assert len(self.storage.repository.data) > 0

    def test_is_linked_via_repository(self):
        """Проверка связей через счетчики репозитория"""
        gram = self.storage.get_range("грамм")
        assert self.service.is_linked(gram.unique_code) is True
        assert self.storage.repository.counts[gram.unique_code] > 0

    def test_delete_linked_entity_blocked_by_repository(self):
        """Блокировка удаления связанной сущности через can_delete"""
        gram = self.storage.get_range("грамм")
        assert self.storage.repository.can_delete(gram) is False
        with pytest.raises(PermissionError):
            self.service.delete_entity("range_model", gram.unique_code)

    def test_create_and_delete_unlinked_entity(self):
        """Создание и удаление несвязанной сущности"""
        payload = {"name": "Новый склад"}
        model = self.service.create_entity("storage_model", payload)
        assert model.unique_code in self.storage.repository.data
        assert self.storage.repository.can_delete(model) is True

        res = self.service.delete_entity("storage_model", model.unique_code)
        assert res is True
        assert model.unique_code not in self.storage.repository.data

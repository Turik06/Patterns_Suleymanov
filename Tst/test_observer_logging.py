import os
import pytest
from Src.Core.abstract_observabile import abstract_observabile
from Src.Core.event_type import event_type
from Src.Core.exception import argument_exception
from Src.Logics.observer import observer
from Src.Logics.logger_service import logger_service
from Src.Logics.storage_manager import storage_manager
from Src.Logics.entity_service import entity_service
from Src.Logics.osv_service import osv_service
from Src.Models.storage_model import storage_model
from Src.Models.transaction_model import transaction_model
from Src.Models.settings_model import settings_model
from main import app


class mock_observer(abstract_observabile):
    """Тестовый наблюдатель для фиксации событий"""

    def __init__(self):
        self.events = []

    def handler(self, event_types: str, params: object = None) -> None:
        self.events.append((event_types, params))


def test_observer_add_and_delete():
    """Проверка добавления и удаления подписчиков из наблюдателя"""
    obs = mock_observer()
    observer.add(obs)
    assert obs in observer.handlers

    # Дубликаты не должны добавляться
    observer.add(obs)
    assert observer.handlers.count(obs) == 1

    observer.delete(obs)
    assert obs not in observer.handlers


def test_observer_validate_type():
    """Проверка, что нельзя добавить неподходящий тип"""
    with pytest.raises(argument_exception):
        observer.add("не_наблюдатель")


def test_observer_create_calls_handler():
    """Проверка рассылки события подписчикам"""
    obs = mock_observer()
    observer.add(obs)

    observer.create(event_type.change_settings(), {"test": 123})
    assert len(obs.events) > 0
    assert obs.events[-1] == (event_type.change_settings(), {"test": 123})

    observer.delete(obs)


def test_logger_service_writes_to_file(tmp_path):
    """Проверка записи логгером в файл"""
    test_log = str(tmp_path / "test.log")
    logger = logger_service()
    logger.log_file = test_log

    observer.create(event_type.storage_operation(), {"action": "test_write"})

    assert os.path.exists(test_log)
    with open(test_log, "r", encoding="utf-8") as f:
        content = f.read()
    assert "storage_operation" in content
    assert "test_write" in content


def test_crud_operations_logging():
    """Проверка логирования CRUD операций"""
    obs = mock_observer()
    observer.add(obs)

    storage = storage_manager()
    storage.first_start()
    service = entity_service(storage)

    # Read
    first_range = list(storage.ranges.values())[0]
    service.get_entity("range_model", first_range.unique_code)

    crud_events = [e for e in obs.events if e[0] == event_type.crud_operation()]
    assert any(e[1].get("action") == "read" for e in crud_events)

    # Create
    created = service.create_entity("range_model", {"name": "новая_ед_изм", "value": 10})
    crud_events = [e for e in obs.events if e[0] == event_type.crud_operation()]
    assert any(e[1].get("action") == "create" and e[1].get("id") == created.unique_code for e in crud_events)

    # Update
    service.update_entity("range_model", created.unique_code, {"name": "обновленная_ед"})
    crud_events = [e for e in obs.events if e[0] == event_type.crud_operation()]
    assert any(e[1].get("action") == "update" for e in crud_events)

    # Delete
    service.delete_entity("range_model", created.unique_code)
    crud_events = [e for e in obs.events if e[0] == event_type.crud_operation()]
    assert any(e[1].get("action") == "delete" for e in crud_events)

    observer.delete(obs)


def test_storage_operations_logging():
    """Проверка логирования складских операций"""
    obs = mock_observer()
    observer.add(obs)

    storage = storage_manager()
    storage.first_start()

    # Добавление склада
    st = storage_model("Тестовый склад")
    storage.add_storage(st)

    # Добавление транзакции
    nom = list(storage.nomenclatures.values())[0]
    rng = list(storage.ranges.values())[0]
    tr = transaction_model(storage=st, nomenclature=nom, range_unit=rng, value=15.0)
    storage.add_transaction(tr)

    # Построение ОСВ
    osv_svc = osv_service(storage)
    osv_svc.build_osv()

    storage_events = [e for e in obs.events if e[0] == event_type.storage_operation()]
    ops = [e[1].get("operation") for e in storage_events]

    assert "add_storage" in ops
    assert "add_transaction" in ops
    assert "build_osv" in ops

    observer.delete(obs)


def test_settings_change_logging():
    """Проверка логирования изменения настроек"""
    obs = mock_observer()
    observer.add(obs)

    settings = settings_model()
    settings.boss_name = "Новый Директор"
    settings.account_name = "Новый Бухгалтер"
    settings.is_first_start = True

    settings_events = [e for e in obs.events if e[0] == event_type.change_settings()]
    fields = [e[1].get("field") for e in settings_events]

    assert "boss_name" in fields
    assert "account_name" in fields
    assert "is_first_start" in fields

    observer.delete(obs)


def test_web_call_logging():
    """Проверка логирования вызовов веб-методов через тестовый клиент"""
    obs = mock_observer()
    observer.add(obs)

    app.testing = True
    client = app.test_client()

    response = client.get("/api/reports/formats")
    assert response.status_code == 200

    web_events = [e for e in obs.events if e[0] == event_type.web_call()]
    assert len(web_events) > 0
    assert web_events[-1][1].get("path") == "/api/reports/formats"
    assert web_events[-1][1].get("status") == 200

    observer.delete(obs)

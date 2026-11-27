import sys
import datetime
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.osv_service import osv_service
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.transaction_model import transaction_model
from Src.Models.osv_row_model import osv_row_model


def create_test_environment():
    """Создает тестовые сущности: склады, единицы измерения и номенклатуру."""
    storage_main = storage_model(name="Основной склад")
    storage_secondary = storage_model(name="Склад филиала")

    range_kg = range_model(name="кг")
    group_food = nomenclature_group_model(name="Продукты")

    nom_flour = nomenclature_model(name="Мука пшеничная", full_name="Мука пшеничная высший сорт", group=group_food, range=range_kg)
    nom_sugar = nomenclature_model(name="Сахар песок", full_name="Сахар белый песок", group=group_food, range=range_kg)

    return storage_main, storage_secondary, range_kg, nom_flour, nom_sugar


def test_osv_row_model_properties_and_calculation():
    """
    Ожидание: osv_row_model корректно сохраняет свойства и считает final_balance.
    """
    # Подготовка
    st, _, rng, nom, _ = create_test_environment()

    # Действие
    row = osv_row_model(
        storage=st,
        nomenclature=nom,
        range_unit=rng,
        start_balance=50.0,
        incoming=120.0,
        outgoing=40.0,
    )
    data = row.to_dict()

    # Проверки
    assert row.storage == st
    assert row.nomenclature == nom
    assert row.range == rng
    assert row.start_balance == 50.0
    assert row.incoming == 120.0
    assert row.outgoing == 40.0
    assert row.final_balance == 130.0
    assert data["start_balance"] == 50.0
    assert data["incoming"] == 120.0
    assert data["outgoing"] == 40.0
    assert data["final_balance"] == 130.0
    assert st in row.references()
    assert nom in row.references()


def test_osv_service_build_without_period():
    """
    Ожидание: При отсутствии периода все транзакции считаются оборотами, входящий остаток равен 0.
    """
    # Подготовка
    st, _, rng, nom, _ = create_test_environment()
    storage = storage_manager()
    storage.clear()

    tx1 = transaction_model(storage=st, nomenclature=nom, range_unit=rng, value=150.0)
    tx2 = transaction_model(storage=st, nomenclature=nom, range_unit=rng, value=-40.0)
    tx3 = transaction_model(storage=st, nomenclature=nom, range_unit=rng, value=-10.0)
    storage.add_transaction(tx1)
    storage.add_transaction(tx2)
    storage.add_transaction(tx3)

    service = osv_service(storage)

    # Действие
    rows = service.build_osv()

    # Проверки
    assert len(rows) == 1
    row = rows[0]
    assert row.start_balance == 0.0
    assert row.incoming == 150.0
    assert row.outgoing == 50.0
    assert row.final_balance == 100.0


def test_osv_service_build_with_period_and_start_balance():
    """
    Ожидание: Транзакции до start_date идут в начальный остаток, внутри периода - в обороты, после end_date - игнорируются.
    """
    # Подготовка
    st, _, rng, nom, _ = create_test_environment()
    storage = storage_manager()
    storage.clear()

    date_before = datetime.datetime(2026, 1, 5, 10, 0, 0)
    date_in_1 = datetime.datetime(2026, 1, 15, 12, 0, 0)
    date_in_2 = datetime.datetime(2026, 1, 20, 15, 0, 0)
    date_after = datetime.datetime(2026, 2, 10, 10, 0, 0)

    # Входящее сальдо до периода
    tx_before = transaction_model(storage=st, nomenclature=nom, range_unit=rng, value=200.0, period=date_before)
    # Движения внутри периода
    tx_in_receipt = transaction_model(storage=st, nomenclature=nom, range_unit=rng, value=100.0, period=date_in_1)
    tx_in_expense = transaction_model(storage=st, nomenclature=nom, range_unit=rng, value=-70.0, period=date_in_2)
    # Транзакция после периода
    tx_after = transaction_model(storage=st, nomenclature=nom, range_unit=rng, value=300.0, period=date_after)

    storage.add_transaction(tx_before)
    storage.add_transaction(tx_in_receipt)
    storage.add_transaction(tx_in_expense)
    storage.add_transaction(tx_after)

    filter_period = filter_dto(start_date="2026-01-10", end_date="2026-01-31")
    service = osv_service(storage)

    # Действие
    rows = service.build_osv(filter_period)

    # Проверки
    assert len(rows) == 1
    row = rows[0]
    assert row.start_balance == 200.0
    assert row.incoming == 100.0
    assert row.outgoing == 70.0
    assert row.final_balance == 230.0


def test_osv_service_filter_by_storage():
    """
    Ожидание: При передаче фильтра по складу ведомость формируется только по выбранному складу.
    """
    # Подготовка
    st1, st2, rng, nom, _ = create_test_environment()
    storage = storage_manager()
    storage.clear()

    tx1 = transaction_model(storage=st1, nomenclature=nom, range_unit=rng, value=80.0)
    tx2 = transaction_model(storage=st2, nomenclature=nom, range_unit=rng, value=40.0)
    storage.add_transaction(tx1)
    storage.add_transaction(tx2)

    filter_st1 = filter_dto.from_dict({"name": "Основной склад", "filter_type_name": "EQUALS"})
    service = osv_service(storage)

    # Действие
    rows = service.build_osv(filter_st1)

    # Проверки
    assert len(rows) == 1
    assert rows[0].storage.name == "Основной склад"
    assert rows[0].incoming == 80.0


def test_osv_service_filter_by_nomenclature():
    """
    Ожидание: Фильтрация по номенклатуре оператором LIKE возвращает только совпадающие строки.
    """
    # Подготовка
    st, _, rng, nom_flour, nom_sugar = create_test_environment()
    storage = storage_manager()
    storage.clear()

    tx_flour = transaction_model(storage=st, nomenclature=nom_flour, range_unit=rng, value=50.0)
    tx_sugar = transaction_model(storage=st, nomenclature=nom_sugar, range_unit=rng, value=30.0)
    storage.add_transaction(tx_flour)
    storage.add_transaction(tx_sugar)

    filter_flour = filter_dto(name="Мука", filter_type=filter_type_enum.LIKE)
    service = osv_service(storage)

    # Действие
    rows = service.build_osv(filter_flour)

    # Проверки
    assert len(rows) == 1
    assert rows[0].nomenclature.name == "Мука пшеничная"
    assert rows[0].incoming == 50.0


def test_osv_service_get_osv_response():
    """
    Ожидание: get_osv_response возвращает список словарей и HTTP-код 200.
    """
    # Подготовка
    st, _, rng, nom, _ = create_test_environment()
    storage = storage_manager()
    storage.clear()

    tx = transaction_model(storage=st, nomenclature=nom, range_unit=rng, value=65.0)
    storage.add_transaction(tx)

    service = osv_service(storage)

    # Действие
    data, status_code = service.get_osv_response()

    # Проверки
    assert status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["incoming"] == 65.0
    assert data[0]["final_balance"] == 65.0

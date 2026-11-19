import sys
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from main import app
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Logics.prototype import prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.transaction_model import transaction_model
from Src.Models.osv_row_model import osv_row_model


def make_nomenclature(name: str, full_name: str = None, group=None, range_unit=None):
    g = group or nomenclature_group_model(name="Группа")
    r = range_unit or range_model(name="кг")
    return nomenclature_model(name=name, full_name=full_name or name, group=g, range=r)


class TestFilterTypeEnum:
    """Тесты перечисления типов фильтрации"""

    def test_from_string_success(self):
        assert filter_type_enum.from_string("EQUALS") == filter_type_enum.EQUALS
        assert filter_type_enum.from_string("like") == filter_type_enum.LIKE
        assert filter_type_enum.from_string(filter_type_enum.LIKE) == filter_type_enum.LIKE

    def test_from_string_default(self):
        assert filter_type_enum.from_string("unknown") == filter_type_enum.EQUALS
        assert filter_type_enum.from_string(None) == filter_type_enum.EQUALS


class TestFilterDto:
    """Тесты DTO фильтрации"""

    def test_filter_item_equals_match(self):
        item = filter_item_dto("name", filter_type_enum.EQUALS, "Мука")
        assert item.is_match("Мука") is True
        assert item.is_match("Сахар") is False

    def test_filter_item_like_match(self):
        item = filter_item_dto("name", filter_type_enum.LIKE, "мук")
        assert item.is_match("Мука пшеничная") is True
        assert item.is_match("Сахар") is False

    def test_filter_dto_from_dict(self):
        data = {
            "name": "Мука",
            "filter_type_name": "LIKE"
        }
        dto = filter_dto.from_dict(data)
        assert len(dto.all_filters) == 1
        assert dto.name == "Мука"
        assert dto.filter_type_name == filter_type_enum.LIKE

    def test_filter_dto_from_domain_model(self):
        nom = make_nomenclature(name="Мука")
        dto = filter_dto.from_domain_model(nom)
        assert dto.name == "Мука"


class TestPrototypeLogic:
    """Тесты логики прототипа и фильтрации"""

    def test_prototype_clone_empty_filter(self):
        items = [
            make_nomenclature(name="Мука"),
            make_nomenclature(name="Сахар")
        ]
        pr = prototype(items)
        cloned = pr.clone()
        assert len(cloned) == 2
        assert cloned is not pr

    def test_prototype_filter_equals(self):
        items = [
            make_nomenclature(name="Мука"),
            make_nomenclature(name="Сахар")
        ]
        pr = prototype(items)
        f = filter_dto.from_dict({"name": "Мука", "filter_type_name": "EQUALS"})
        cloned = pr.clone(f)
        assert len(cloned) == 1
        assert cloned[0].name == "Мука"

    def test_prototype_filter_like(self):
        items = [
            make_nomenclature(name="Мука пшеничная"),
            make_nomenclature(name="Мука ржаная"),
            make_nomenclature(name="Сахар")
        ]
        pr = prototype(items)
        f = filter_dto.from_dict({"name": "Мука", "filter_type_name": "LIKE"})
        cloned = pr.clone(f)
        assert len(cloned) == 2

    def test_prototype_recursive_filter_range(self):
        gram = range_model(name="грамм")
        kg = range_model(name="килограмм", conversion_factor=1000, base_range=gram)
        pr = prototype([kg, gram])

        f = filter_dto.from_dict({"name": "грамм", "filter_type_name": "EQUALS"})
        cloned = pr.clone(f)
        assert len(cloned) == 2

    def test_prototype_recursive_filter_group(self):
        parent = nomenclature_group_model(name="Ингредиенты")
        child = nomenclature_group_model(name="Бакалея", parent=parent)
        other = nomenclature_group_model(name="Напитки")
        pr = prototype([child, other])

        f = filter_dto.from_dict({"name": "Ингредиенты", "filter_type_name": "EQUALS"})
        cloned = pr.clone(f)
        assert len(cloned) == 1
        assert cloned[0].name == "Бакалея"

    def test_prototype_recursive_filter_nomenclature_by_group(self):
        grp = nomenclature_group_model(name="Специи")
        nom = make_nomenclature(name="Перец", group=grp)
        nom2 = make_nomenclature(name="Вода")
        pr = prototype([nom, nom2])

        f = filter_dto.from_dict({"name": "Специи", "filter_type_name": "EQUALS"})
        cloned = pr.clone(f)
        assert len(cloned) == 1
        assert cloned[0].name == "Перец"


class TestPrototypeOsv:
    """Тесты формирования оборотно-сальдовой ведомости"""

    def test_create_osv_calculation(self):
        wh = storage_model(name="Основной склад")
        rng = range_model(name="кг")
        nom = make_nomenclature(name="Мука", range_unit=rng)

        tx1 = transaction_model(storage=wh, nomenclature=nom, range_unit=rng, value=100.0)
        tx2 = transaction_model(storage=wh, nomenclature=nom, range_unit=rng, value=-30.0)
        tx3 = transaction_model(storage=wh, nomenclature=nom, range_unit=rng, value=-20.0)

        pr = prototype([tx1, tx2, tx3])
        osv = pr.create_osv()
        assert len(osv) == 1
        row = osv[0]
        assert row.incoming == 100.0
        assert row.outgoing == 50.0
        assert row.final_balance == 50.0
        assert row.to_dict()["incoming"] == 100.0
        assert row.to_dict()["final_balance"] == 50.0

    def test_osv_references_and_filtering(self):
        wh1 = storage_model(name="Склад 1")
        wh2 = storage_model(name="Склад 2")
        rng = range_model(name="кг")
        nom = make_nomenclature(name="Сахар", range_unit=rng)

        tx1 = transaction_model(storage=wh1, nomenclature=nom, range_unit=rng, value=50.0)
        tx2 = transaction_model(storage=wh2, nomenclature=nom, range_unit=rng, value=30.0)

        pr = prototype([tx1, tx2])
        osv = pr.create_osv()
        assert len(osv) == 2

        f = filter_dto.from_dict({"name": "Склад 1", "filter_type_name": "EQUALS"})
        filtered_osv = osv.clone(f)
        assert len(filtered_osv) == 1
        assert filtered_osv[0].storage.name == "Склад 1"


class TestPrototypeApi:
    """Тесты REST API для фильтрации и ОСВ"""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        app.testing = True
        self.client = app.test_client()
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()

    def test_filter_api_endpoint_success(self):
        payload = {"name": "мука", "filter_type_name": "LIKE"}
        response = self.client.post("/api/filter/nomenclature", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_filter_api_endpoint_unknown_domain(self):
        response = self.client.post("/api/filter/unknown_category", json={})
        assert response.status_code == 400

    def test_osv_api_endpoint(self):
        wh = list(self.storage.storages.values())[0]
        nom = list(self.storage.nomenclatures.values())[0]
        tx = transaction_model(storage=wh, nomenclature=nom, range_unit=nom.range, value=75.0)
        self.storage.save_entity(tx)

        response = self.client.post("/api/osv", json={})
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "incoming" in data[0]
        assert "final_balance" in data[0]

    def test_turnarounds_alias_api_endpoint(self):
        response = self.client.post("/api/turnarounds", json={})
        assert response.status_code == 200

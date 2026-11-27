import sys
import datetime
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from main import app
from Src.Core.common import common
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
        assert filter_type_enum.from_string(None) == filter_type_enum.EQUALS
        assert filter_type_enum.from_string("") == filter_type_enum.EQUALS
        with pytest.raises(ValueError):
            filter_type_enum.from_string("unknown")
        with pytest.raises(ValueError):
            filter_type_enum.from_string("DISLIKE")


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

    def test_parse_date_helper(self):
        now = datetime.datetime.now()
        today = datetime.date.today()
        assert common.parse_date(now) == now
        assert common.parse_date(today) == today
        assert common.parse_date("2026-01-15") == datetime.datetime(2026, 1, 15, 0, 0)
        assert common.parse_date(None) is None
        assert common.parse_date("") is None
        assert common.parse_date("invalid") is None
        assert common.parse_date(123) is None
        # Проверяем статический метод самого DTO
        assert filter_dto.parse_date("2026-01-15") == datetime.datetime(2026, 1, 15, 0, 0)


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

    def test_prototype_filter_by_value_and_conversion_factor(self):
        gram = range_model(name="грамм", conversion_factor=1)
        kg = range_model(name="килограмм", conversion_factor=1000, base_range=gram)
        pr = prototype([gram, kg])

        # Фильтрация по value числом
        f_val = filter_dto(filters=[filter_item_dto("value", filter_type_enum.EQUALS, 1000)])
        assert len(pr.clone(f_val)) == 1
        assert pr.clone(f_val)[0].name == "килограмм"

        # Фильтрация по conversion_factor строкой
        f_str = filter_dto(filters=[filter_item_dto("conversion_factor", filter_type_enum.EQUALS, "1000")])
        assert len(pr.clone(f_str)) == 1
        assert pr.clone(f_str)[0].name == "килограмм"

    def test_prototype_filter_dotted_path(self):
        gram = range_model(name="грамм", conversion_factor=1)
        kg = range_model(name="килограмм", conversion_factor=1000, base_range=gram)
        pr = prototype([gram, kg])

        # Фильтрация по вложенному свойству base_range.name
        f_nested = filter_dto(filters=[filter_item_dto("base_range.name", filter_type_enum.EQUALS, "грамм")])
        assert len(pr.clone(f_nested)) == 1
        assert pr.clone(f_nested)[0].name == "килограмм"

        # Фильтрация по вложенному свойству base_range.value
        f_nested_val = filter_dto(filters=[filter_item_dto("base_range.value", filter_type_enum.EQUALS, 1)])
        assert len(pr.clone(f_nested_val)) == 1
        assert pr.clone(f_nested_val)[0].name == "килограмм"

    def test_prototype_get_filterable_fields(self):
        gram = range_model(name="грамм", conversion_factor=1)
        kg = range_model(name="килограмм", conversion_factor=1000, base_range=gram)
        pr = prototype([gram, kg])

        fields = pr.filterable_fields
        assert "name" in fields
        assert "value" in fields
        assert "conversion_factor" in fields
        assert "base_range.name" in fields
        assert "base_range.value" in fields


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

    def test_filter_api_invalid_payload_returns_400(self):
        response = self.client.post("/api/filter/nomenclature", json=[1, 2, 3])
        assert response.status_code == 400

    def test_filter_api_invalid_operation_returns_400(self):
        response = self.client.post("/api/filter/nomenclature", json={"name": "мука", "filter_type": "UNKNOWN"})
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

    def test_osv_api_invalid_payload_returns_400(self):
        response = self.client.post("/api/osv", json=[1, 2, 3])
        assert response.status_code == 400

    def test_osv_api_with_period(self):
        wh = list(self.storage.storages.values())[0]
        nom = list(self.storage.nomenclatures.values())[0]
        d_old = datetime.datetime(2025, 12, 1, 10, 0, 0)
        d_new = datetime.datetime(2026, 1, 15, 10, 0, 0)
        tx1 = transaction_model(storage=wh, nomenclature=nom, range_unit=nom.range, value=100.0, period=d_old)
        tx2 = transaction_model(storage=wh, nomenclature=nom, range_unit=nom.range, value=50.0, period=d_new)
        self.storage.save_entity(tx1)
        self.storage.save_entity(tx2)

        payload = {"start_date": "2026-01-01", "end_date": "2026-01-31"}
        response = self.client.post("/api/osv", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        target = next((item for item in data if item["nomenclature"] == nom.name), None)
        assert target is not None
        assert target["start_balance"] >= 100.0
        assert target["incoming"] >= 50.0

    def test_get_filter_fields_api_endpoint(self):
        response = self.client.get("/api/filter/range/fields")
        assert response.status_code == 200
        data = response.get_json()
        assert "fields" in data
        assert "value" in data["fields"]
        assert "conversion_factor" in data["fields"]
        assert "base_range.name" in data["fields"]

    def test_get_filter_fields_unknown_domain_returns_400(self):
        response = self.client.get("/api/filter/unknown_entity/fields")
        assert response.status_code == 400

    def test_filter_api_endpoint_by_value(self):
        payload = {
            "filters": [
                {"field_name": "value", "filter_type": "EQUALS", "value": 1000}
            ]
        }
        response = self.client.post("/api/filter/range", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        names = [x.get("name") for x in data]
        assert "килограмм" in names or "литр" in names

    def test_filter_api_endpoint_by_nested_path(self):
        payload = {
            "filters": [
                {"field_name": "base_range.name", "filter_type": "EQUALS", "value": "грамм"}
            ]
        }
        response = self.client.post("/api/filter/range", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        names = [x.get("name") for x in data]
        assert "килограмм" in names

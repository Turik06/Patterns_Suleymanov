from Src.Core.abstract_prototype import abstract_prototype
from Src.Dtos.filter_dto import filter_dto


class prototype(abstract_prototype):
    """Прототип для фильтрации коллекций доменных моделей."""

    def __init__(self, data: list = None):
        self._data = list(data) if data is not None else []

    @property
    def data(self) -> list:
        return self._data

    @data.setter
    def data(self, val: list):
        self._data = list(val) if val is not None else []

    def __getattr__(self, name: str):
        if name.lstrip("_") == "data":
            return self._data
        raise AttributeError(name)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item):
        return self._data[item]

    @staticmethod
    def _extract_values(obj, field_name: str, visited: set = None) -> list:
        if obj is None:
            return []
        if visited is None:
            visited = set()

        obj_id = id(obj)
        if obj_id in visited:
            return []
        visited.add(obj_id)

        values = []

        val = getattr(obj, field_name, None)
        if val is not None and not callable(val):
            values.append(val)

        if hasattr(obj, "references") and callable(obj.references):
            for ref in obj.references():
                values.extend(prototype._extract_values(ref, field_name, visited))

        return values

    def clone(self, filter_model: filter_dto = None) -> "prototype":
        """Создает копию прототипа с отфильтрованными данными."""
        if not filter_model:
            return prototype(self._data)

        filter_items = filter_model.all_filters if hasattr(filter_model, "all_filters") else list(filter_model)
        if not filter_items:
            return prototype(self._data)

        filtered = []
        for obj in self._data:
            match_all = True
            for item in filter_items:
                values = self._extract_values(obj, item.field_name)
                if not any(item.is_match(v) for v in values):
                    match_all = False
                    break

            if match_all:
                filtered.append(obj)

        return prototype(filtered)

    def create_osv(self) -> "prototype":
        """Формирует оборотно-сальдовую ведомость на основе транзакций"""
        from Src.Models.osv_row_model import osv_row_model

        grouped = {}
        for tr in self._data:
            storage = getattr(tr, "storage", None)
            nom = getattr(tr, "nomenclature", None)
            rng = getattr(tr, "range", None)
            val = float(getattr(tr, "value", 0.0))

            key = (getattr(storage, "id", None), getattr(nom, "id", None), getattr(rng, "id", None))
            if key not in grouped:
                grouped[key] = {
                    "storage": storage,
                    "nomenclature": nom,
                    "range": rng,
                    "incoming": 0.0,
                    "outgoing": 0.0,
                }

            if val > 0:
                grouped[key]["incoming"] += val
            else:
                grouped[key]["outgoing"] += abs(val)

        rows = [
            osv_row_model(
                storage=item["storage"],
                nomenclature=item["nomenclature"],
                range_unit=item["range"],
                incoming=item["incoming"],
                outgoing=item["outgoing"],
            )
            for item in grouped.values()
        ]
        return prototype(rows)


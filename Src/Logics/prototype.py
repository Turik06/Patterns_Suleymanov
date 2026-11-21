from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.common import common
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

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item):
        return self._data[item]

    @staticmethod
    def _resolve_nested_path(source, parts: list[str]) -> list:
        """Достаем значение по цепочке полей через точку"""
        if not parts or source is None:
            return []

        head = parts[0]
        tail = parts[1:]

        if isinstance(source, (list, tuple, set)):
            results = []
            for item in source:
                results.extend(prototype._resolve_nested_path(item, parts))
            return results

        val = getattr(source, head, None)
        if val is None or callable(val):
            return []

        if not tail:
            if isinstance(val, (list, tuple, set)):
                return list(val)
            return [val]

        return prototype._resolve_nested_path(val, tail)

    @staticmethod
    def _extract_values(obj, field_name: str, visited: set = None) -> list:
        if obj is None:
            return []

        # если в имени поля есть точка, идем по цепочке вложенных объектов
        if "." in field_name:
            parts = field_name.split(".")
            return prototype._resolve_nested_path(obj, parts)

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

    @staticmethod
    def get_filterable_fields(source, max_depth: int = 2) -> list[str]:
        """Собираем список всех полей модели, по которым можно фильтровать."""
        from Src.Core.common import common
        from Src.Core.abstract_model import name_id

        if not source:
            return []

        items = source if isinstance(source, (list, tuple, set)) else [source]
        all_fields = set()

        def _inspect(sample, depth, prefix, visited):
            if sample is None or depth < 0:
                return
            v_key = (type(sample), getattr(sample, "id", None) if not isinstance(sample, type) else None)
            if v_key in visited:
                return
            visited.add(v_key)

            if isinstance(sample, type):
                fields = [f for f in dir(sample) if isinstance(getattr(sample, f, None), property)]
            else:
                try:
                    fields = common.get_fields(sample)
                except Exception:
                    fields = [f for f in dir(sample) if not f.startswith("_") and not callable(getattr(sample, f, None))]

            for f in fields:
                field_path = f"{prefix}{f}"
                all_fields.add(field_path)
                val = getattr(sample, f, None) if not isinstance(sample, type) else None
                if isinstance(val, name_id) and depth > 0:
                    _inspect(val, depth - 1, f"{field_path}.", visited.copy())
                elif isinstance(val, (list, tuple, set)) and val and depth > 0:
                    for elem in val:
                        if isinstance(elem, name_id):
                            _inspect(elem, depth - 1, f"{field_path}.", visited.copy())

        for item in items:
            _inspect(item, max_depth, "", set())

        return sorted(list(all_fields))

    @property
    def filterable_fields(self) -> list[str]:
        """Список доступных полей для фильтрации."""
        return prototype.get_filterable_fields(self._data)

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

    def create_osv(self, start_date=None, end_date=None) -> "prototype":
        """Сформировать ОСВ по транзакциям."""
        from Src.Models.osv_row_model import osv_row_model

        p_start = common.parse_date(start_date)
        p_end = common.parse_date(end_date)
        d_start = p_start.date() if hasattr(p_start, "date") else p_start
        d_end = p_end.date() if hasattr(p_end, "date") else p_end

        grouped = {}
        for tr in self._data:
            storage = getattr(tr, "storage", None)
            nom = getattr(tr, "nomenclature", None)
            rng = getattr(tr, "range", None)
            val = float(getattr(tr, "value", 0.0))
            period = getattr(tr, "period", None)
            tr_date = period.date() if hasattr(period, "date") else period

            key = (getattr(storage, "id", None), getattr(nom, "id", None), getattr(rng, "id", None))
            if key not in grouped:
                grouped[key] = {
                    "storage": storage,
                    "nomenclature": nom,
                    "range": rng,
                    "start_balance": 0.0,
                    "incoming": 0.0,
                    "outgoing": 0.0,
                }

            if d_start and tr_date and tr_date < d_start:
                # до периода - начальный остаток
                grouped[key]["start_balance"] += val
            elif d_end and tr_date and tr_date > d_end:
                # после периода - пропускаем
                continue
            else:
                # внутри периода - обороты
                if val > 0:
                    grouped[key]["incoming"] += val
                else:
                    grouped[key]["outgoing"] += abs(val)

        rows = [
            osv_row_model(
                storage=item["storage"],
                nomenclature=item["nomenclature"],
                range_unit=item["range"],
                start_balance=item["start_balance"],
                incoming=item["incoming"],
                outgoing=item["outgoing"],
            )
            for item in grouped.values()
        ]
        return prototype(rows)

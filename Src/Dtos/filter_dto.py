import datetime
from typing import Optional
from Src.Core.common import common
from Src.Dtos.filter_type_enum import filter_type_enum


class filter_item_dto:
    """Критерий фильтрации: поле, тип сравнения и значение."""

    def __init__(self, field_name: str = "", filter_type=filter_type_enum.EQUALS, value=None):
        self._field_name = str(field_name or "")
        self._filter_type = filter_type_enum.from_string(filter_type)
        self._value = value

    @property
    def field_name(self) -> str:
        return self._field_name

    @field_name.setter
    def field_name(self, val: str):
        self._field_name = str(val or "")

    @property
    def filter_type(self) -> filter_type_enum:
        return self._filter_type

    @filter_type.setter
    def filter_type(self, val):
        self._filter_type = filter_type_enum.from_string(val)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def is_match(self, val) -> bool:
        if val is None or self.value is None:
            return False

        d_val = common.parse_date(val)
        d_target = common.parse_date(self.value)
        if d_val is not None and d_target is not None:
            if self.filter_type == filter_type_enum.EQUALS:
                return d_val == d_target
            if self.filter_type == filter_type_enum.LESS_THAN:
                return d_val < d_target
            if self.filter_type == filter_type_enum.LESS_EQUALS:
                return d_val <= d_target
            if self.filter_type == filter_type_enum.GREATER_THAN:
                return d_val > d_target
            if self.filter_type == filter_type_enum.GREATER_EQUALS:
                return d_val >= d_target

        # если оба значения числа, сравниваем как числа
        try:
            num_val = float(val)
            num_target = float(self.value)
            if self.filter_type == filter_type_enum.EQUALS:
                return num_val == num_target
            if self.filter_type == filter_type_enum.LESS_THAN:
                return num_val < num_target
            if self.filter_type == filter_type_enum.LESS_EQUALS:
                return num_val <= num_target
            if self.filter_type == filter_type_enum.GREATER_THAN:
                return num_val > num_target
            if self.filter_type == filter_type_enum.GREATER_EQUALS:
                return num_val >= num_target
        except (ValueError, TypeError):
            pass

        s_val = str(val).strip().lower()
        s_target = str(self.value).strip().lower()

        if self.filter_type == filter_type_enum.LIKE:
            return s_target in s_val

        return s_val == s_target

    def to_dict(self) -> dict:
        return {
            "field_name": self.field_name,
            "filter_type": str(self.filter_type),
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "filter_item_dto":
        if not isinstance(data, dict):
            return cls()
        field_name = data.get("field_name") if "field_name" in data else data.get("name", "")
        f_type = data.get("filter_type", filter_type_enum.EQUALS)
        return cls(
            field_name=field_name,
            filter_type=f_type,
            value=data.get("value"),
        )


class filter_dto:
    """Набор параметров фильтрации."""

    def __init__(
        self,
        name: str = "",
        unique_code: str = "",
        filter_type=filter_type_enum.EQUALS,
        filters: list = None,
        start_date=None,
        end_date=None,
    ):
        self._name = str(name or "")
        self._unique_code = str(unique_code or "")
        self._filter_type = filter_type_enum.from_string(filter_type)
        self._filters = list(filters) if filters else []
        self._start_date = common.parse_date(start_date)
        self._end_date = common.parse_date(end_date)

    @staticmethod
    def parse_date(val):
        """Парсинг даты через общий хелпер."""
        return common.parse_date(val)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        self._name = str(val or "")

    @property
    def unique_code(self) -> str:
        return self._unique_code

    @unique_code.setter
    def unique_code(self, val: str):
        self._unique_code = str(val or "")

    @property
    def filter_type(self) -> filter_type_enum:
        return self._filter_type

    @filter_type.setter
    def filter_type(self, val):
        self._filter_type = filter_type_enum.from_string(val)

    @property
    def filter_type_name(self) -> filter_type_enum:
        return self._filter_type

    @filter_type_name.setter
    def filter_type_name(self, val):
        self._filter_type = filter_type_enum.from_string(val)

    @property
    def filters(self) -> list:
        return self._filters

    @filters.setter
    def filters(self, val: list):
        self._filters = list(val) if val else []

    @property
    def start_date(self) -> Optional[datetime.datetime]:
        return self._start_date

    @start_date.setter
    def start_date(self, val):
        self._start_date = common.parse_date(val)

    @property
    def end_date(self) -> Optional[datetime.datetime]:
        return self._end_date

    @end_date.setter
    def end_date(self, val):
        self._end_date = common.parse_date(val)

    def add(self, item: filter_item_dto):
        self._filters.append(item)

    @property
    def all_filters(self) -> list[filter_item_dto]:
        result = []
        if self._name:
            result.append(filter_item_dto("name", self._filter_type, self._name))
        if self._unique_code:
            result.append(filter_item_dto("unique_code", filter_type_enum.EQUALS, self._unique_code))

        for f in self._filters:
            if isinstance(f, dict):
                result.append(filter_item_dto.from_dict(f))
            elif isinstance(f, filter_item_dto):
                result.append(f)
        return result

    def to_dict(self) -> dict:
        res = {"filter_type": str(self._filter_type)}
        if self._name:
            res["name"] = self._name
        if self._unique_code:
            res["unique_code"] = self._unique_code
        if self._filters:
            res["filters"] = [f.to_dict() if hasattr(f, "to_dict") else f for f in self._filters]
        if self._start_date:
            res["start_date"] = self._start_date.isoformat()
        if self._end_date:
            res["end_date"] = self._end_date.isoformat()
        return res

    @classmethod
    def from_dict(cls, data: dict) -> "filter_dto":
        if not isinstance(data, dict):
            return cls()
        code = data.get("unique_code") or data.get("id", "")
        f_type = data.get("filter_type") or data.get("filter_type_name") or filter_type_enum.EQUALS
        raw_items = data.get("filters", [])
        items = [filter_item_dto.from_dict(x) if isinstance(x, dict) else x for x in raw_items]
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        return cls(
            name=data.get("name", ""),
            unique_code=code,
            filter_type=f_type,
            filters=items,
            start_date=start_date,
            end_date=end_date,
        )

    @classmethod
    def from_domain_model(cls, model) -> "filter_dto":
        if not model:
            return cls()
        name = getattr(model, "name", "")
        code = getattr(model, "unique_code", getattr(model, "id", ""))
        return cls(name=name, unique_code=code, filter_type=filter_type_enum.EQUALS)

    def __iter__(self):
        return iter(self.all_filters)

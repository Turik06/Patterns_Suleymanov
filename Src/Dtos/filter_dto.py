from Src.Dtos.filter_type_enum import filter_type_enum


class filter_item_dto:
    """Критерий фильтрации: поле, тип сравнения и значение."""

    def __init__(self, field_name: str = "", filter_type=filter_type_enum.EQUALS, value=None):
        self._field_name = field_name
        self._filter_type = filter_type_enum.from_string(filter_type)
        self._value = value

    @property
    def field_name(self) -> str:
        return self._field_name

    @field_name.setter
    def field_name(self, val: str):
        self._field_name = val

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

    def __getattr__(self, name: str):
        key = name.lstrip("_")
        if key in ("field_name", "filter_type", "value"):
            return getattr(self, f"_{key}")
        raise AttributeError(name)

    def __setattr__(self, name: str, val):
        key = name.lstrip("_")
        if key == "filter_type":
            val = filter_type_enum.from_string(val)
        if key in ("field_name", "filter_type", "value"):
            super().__setattr__(f"_{key}", val)
        else:
            super().__setattr__(name, val)

    def is_match(self, val) -> bool:
        if val is None or self.value is None:
            return False

        if isinstance(val, (int, float)) and isinstance(self.value, (int, float)):
            return val == self.value

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
        return cls(
            field_name=data.get("field_name", data.get("name", "")),
            filter_type=data.get("filter_type", filter_type_enum.EQUALS),
            value=data.get("value"),
        )


class filter_dto:
    """Набор параметров фильтрации."""

    def __init__(self, name: str = "", unique_code: str = "", filter_type=filter_type_enum.EQUALS, filters: list = None):
        self._name = name
        self._unique_code = unique_code
        self._filter_type = filter_type_enum.from_string(filter_type)
        self._filters = list(filters) if filters else []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        self._name = val or ""

    @property
    def unique_code(self) -> str:
        return self._unique_code

    @unique_code.setter
    def unique_code(self, val: str):
        self._unique_code = val or ""

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

    def __getattr__(self, name: str):
        key = name.lstrip("_")
        if key in ("name", "unique_code", "filter_type", "filter_type_name", "filters"):
            return getattr(self, "_filter_type" if key == "filter_type_name" else f"_{key}")
        raise AttributeError(name)

    def __setattr__(self, name: str, val):
        key = name.lstrip("_")
        if key in ("filter_type", "filter_type_name"):
            val = filter_type_enum.from_string(val)
            super().__setattr__("_filter_type", val)
            return
        elif key == "filters":
            val = list(val) if val else []
        if key in ("name", "unique_code", "filters"):
            super().__setattr__(f"_{key}", val)
        else:
            super().__setattr__(name, val)

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
        return res

    @classmethod
    def from_dict(cls, data: dict) -> "filter_dto":
        if not isinstance(data, dict):
            return cls()
        code = data.get("unique_code") or data.get("id", "")
        f_type = data.get("filter_type") or data.get("filter_type_name") or filter_type_enum.EQUALS
        raw_items = data.get("filters", [])
        items = [filter_item_dto.from_dict(x) if isinstance(x, dict) else x for x in raw_items]
        return cls(name=data.get("name", ""), unique_code=code, filter_type=f_type, filters=items)

    @classmethod
    def from_domain_model(cls, model) -> "filter_dto":
        if not model:
            return cls()
        name = getattr(model, "name", "")
        code = getattr(model, "unique_code", getattr(model, "id", ""))
        return cls(name=name, unique_code=code, filter_type=filter_type_enum.EQUALS)

    def __iter__(self):
        return iter(self.all_filters)

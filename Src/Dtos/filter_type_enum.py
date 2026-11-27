from enum import Enum


class filter_type_enum(str, Enum):
    """Типы фильтрации."""

    EQUALS = "EQUALS"
    LIKE = "LIKE"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUALS = "LESS_EQUALS"
    GREATER_EQUALS = "GREATER_EQUALS"

    @classmethod
    def from_string(cls, val):
        """Получить enum из строки или экземпляра filter_type_enum."""
        if isinstance(val, filter_type_enum):
            return val
        if val is None:
            return cls.EQUALS
        s = str(val).strip().upper()
        if not s:
            return cls.EQUALS
        if s in ("EQUALS", "EQ", "1"):
            return cls.EQUALS
        if s in ("LIKE", "2"):
            return cls.LIKE
        if s in ("LESS_THAN", "LT", "<"):
            return cls.LESS_THAN
        if s in ("GREATER_THAN", "GT", ">"):
            return cls.GREATER_THAN
        if s in ("LESS_EQUALS", "LE", "<="):
            return cls.LESS_EQUALS
        if s in ("GREATER_EQUALS", "GE", ">="):
            return cls.GREATER_EQUALS
        raise ValueError(
            f"Неизвестный тип фильтрации '{val}'. Поддерживаются: EQUALS, LIKE, LESS_THAN, GREATER_THAN, LESS_EQUALS, GREATER_EQUALS"
        )

    def __eq__(self, other):
        """Сравнение со строками без учета регистра."""
        if isinstance(other, filter_type_enum):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.strip().upper()
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self.value

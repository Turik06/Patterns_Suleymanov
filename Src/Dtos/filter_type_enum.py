from enum import Enum


class filter_type_enum(str, Enum):
    """Типы фильтрации."""

    EQUALS = "EQUALS"
    LIKE = "LIKE"

    @classmethod
    def from_string(cls, val):
        """Получить enum из строки."""
        if not val:
            return cls.EQUALS
        s = str(val).strip().upper()
        return cls.LIKE if "LIKE" in s else cls.EQUALS

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

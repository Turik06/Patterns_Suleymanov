from abc import ABC, abstractmethod


class abstract_prototype(ABC):
    """Абстрактный класс прототипа."""

    @abstractmethod
    def clone(self, filter) -> "abstract_prototype":
        pass
